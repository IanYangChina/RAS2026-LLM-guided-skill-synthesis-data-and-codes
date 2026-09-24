## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | 7 | 0.9156 | 0.99 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | 6 | 0.9319 | 0.99 | ✅ accepted |
| 9 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8963 | 0.94 | ❌ rejected |
| 8 | grasp → approach → insert → release → retract | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | grasp_success | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2855 | 0.86 | ❌ rejected |
| 7 | approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.4161 | 0.89 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.99). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.916) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_hole
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.16
  weight: 0.3
- id: insertion_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.16
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_above_hole
- id: insert_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 15.0
      - 40.0
      default: 25.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: insertion_progress
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: impedance_control
  termination: contact_lost
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.16], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **insert_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.18, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.916
- **task_score** (E): 0.990
- **fitness_score**: 0.990  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.306
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1014 |
| insert_1 | 1.00 | 1.00 | 0.1275 |
| retract_1 | 1.00 | 0.00 | 0.0725 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, 0.001, 0.199) | (0.504, -0.000, 0.340)→(0.508, 0.001, 0.239) | 0.260→0.159 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | push | 1.00 / force_exceeded | (0.504, 0.001, 0.199)→(0.500, 0.001, 0.072) | (0.508, 0.001, 0.239)→(0.505, 0.001, 0.111) | 0.159→0.032 | 1.00 / 1.000 | 1345.832 | 0.000 |
| retract_1 | retract | 1.00 / step_budget | (0.500, 0.001, 0.072)→(0.496, 0.001, 0.144) | (0.505, 0.001, 0.111)→(0.502, 0.001, 0.184) | 0.032→0.104 | 0.00 / 0.000 | 0.000 | 65.717 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.994
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.994
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.994
- **Median Q (composite search score)**: 0.944
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.377


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5e5af3f51d5f63e3a348998ea00f94a7255959965642a40069d0a7b5ef8ede34`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `cc7f64fba434a86728ba6288ab9746a03660fc43702ba486c544717f06e4937d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37374,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06466,"approach_1.lateral_x":-0.01854,"approach_1.lateral_y":-0.02491,"insert_1.force_threshold":18.50688,"insert_1.guard_force_limit":41.43467,"insert_1.insertion_depth":0.16856,"retract_1.retract_speed":0.05645},"optimized_scores":{"best_composite_score":0.94352,"best_fitness_score":0.99019,"best_task_score":0.99019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.51228,-0.00537,0.07993],"force_p95":55.62857,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.00336,"mean_force":19.33345,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49827,-0.00031,0.08165]}],"total_contact_groups":1},"final_pose_error":0.11249,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.49537,-0.00035,0.16928],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":66.00336,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,-0.00025,0.23893],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15908,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.50226,-0.00025,0.19919],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.50361,-0.0003,0.1214],"object_pos_start":[0.50684,-0.00025,0.23893],"object_to_goal_dist_end":0.04156,"object_to_goal_dist_start":0.15908,"object_z_max":0.23893,"peak_contact_force":58.27058,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.49858,-0.00031,0.08172],"tcp_start":[0.50226,-0.00025,0.19919],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50086,-0.00033,0.2089],"object_pos_start":[0.50361,-0.0003,0.1214],"object_to_goal_dist_end":0.1289,"object_to_goal_dist_start":0.04156,"object_z_max":0.20879,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":15.0,"raw_peak_contact_force":66.00336,"tcp_end":[0.49537,-0.00035,0.16928],"tcp_start":[0.49858,-0.00031,0.08172],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40187,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06358,"approach_1.lateral_x":0.00604,"approach_1.lateral_y":0.01239,"insert_1.force_threshold":18.1116,"insert_1.guard_force_limit":34.18273,"insert_1.insertion_depth":0.16407,"retract_1.retract_speed":0.04837},"optimized_scores":{"best_composite_score":0.94772,"best_fitness_score":0.99438,"best_task_score":0.99438},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.51586,-0.00017,0.0499],"force_p95":66.06938,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.54787,"mean_force":33.5619,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50098,-0.00023,0.05169]}],"total_contact_groups":1},"final_pose_error":0.1235,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49757,-0.00027,0.12828],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":73.54787,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.50956,-0.00015,0.23893],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15921,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.50498,-0.00016,0.19919],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,-0.00021,0.09141],"object_pos_start":[0.50956,-0.00015,0.23893],"object_to_goal_dist_end":0.01295,"object_to_goal_dist_start":0.15921,"object_z_max":0.23893,"peak_contact_force":62.42348,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.50108,-0.00022,0.05173],"tcp_start":[0.50498,-0.00016,0.19919],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,-0.00025,0.1679],"object_pos_start":[0.50611,-0.00021,0.09141],"object_to_goal_dist_end":0.08795,"object_to_goal_dist_start":0.01295,"object_z_max":0.16781,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":9.0,"raw_peak_contact_force":73.54787,"tcp_end":[0.49757,-0.00027,0.12828],"tcp_start":[0.50108,-0.00022,0.05173],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13492,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03747,"approach_1.lateral_x":-0.00236,"approach_1.lateral_y":-0.02839,"insert_1.force_threshold":36.76401,"insert_1.guard_force_limit":38.66777,"insert_1.insertion_depth":0.12583,"retract_1.retract_speed":0.02607},"optimized_scores":{"best_composite_score":0.85561,"best_fitness_score":0.98561,"best_task_score":0.98561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.51463,0.00178,0.07993],"force_p95":51.61368,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.60032,"mean_force":28.64065,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49979,0.0027,0.08175]}],"total_contact_groups":1},"final_pose_error":0.14686,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49652,0.00265,0.13498],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":3916.80082,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50832,0.0028,0.23885],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1591,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.50375,0.00279,0.19912],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":810.0,"object_pos_end":[0.50499,0.00273,0.12149],"object_pos_start":[0.50832,0.0028,0.23885],"object_to_goal_dist_end":0.04188,"object_to_goal_dist_start":0.1591,"object_z_max":0.23885,"peak_contact_force":3916.80082,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.49995,0.00271,0.08181],"tcp_start":[0.50375,0.00279,0.19912],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50202,0.00267,0.1746],"object_pos_start":[0.50499,0.00273,0.12149],"object_to_goal_dist_end":0.09466,"object_to_goal_dist_start":0.04188,"object_z_max":0.17456,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":57.60032,"tcp_end":[0.49652,0.00265,0.13498],"tcp_start":[0.49995,0.00271,0.08181],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```