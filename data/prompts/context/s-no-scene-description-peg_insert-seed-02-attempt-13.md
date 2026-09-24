## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0453 | 0.95 | ❌ rejected |
| 12 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0454 | 0.95 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0922 | 0.95 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0057 | 0.94 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.3063 | 0.92 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=-0.045) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: align_1
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.015
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: insert_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_guard_threshold:
      type: scalar
      range:
      - 25.0
      - 45.0
      default: 35.0
      binds_to:
      - path: guards.insertion_force_guard.threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: insertion_force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_guard_threshold: status=consumed; consumers=guards.insertion_force_guard.threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=insertion_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.045
- **task_score** (E): 0.949
- **fitness_score**: 0.385  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0617 |
| align_1 | 1.00 | 0.67 | 0.1173 |
| insert_1 | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.008, 0.244) | (0.504, -0.000, 0.340)→(0.503, -0.008, 0.284) | 0.260→0.205 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.008, 0.244)→(0.485, -0.021, 0.129) | (0.503, -0.008, 0.284)→(0.523, -0.020, 0.118) | 0.205→0.055 | 0.67 / 0.667 | 195.657 | 1344.252 |
| insert_1 | push | 0.00 / guard_failure | (0.485, -0.021, 0.129)→(0.485, -0.021, 0.129) | (0.523, -0.020, 0.118)→(0.523, -0.020, 0.118) | 0.055→0.055 | 1.00 / 1.000 | 367.721 | 367.721 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.996
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.996
- phase_score: 0.008
- phase_breakdown.insertion_score: 0.000
- phase_breakdown.pre_contact_score: 0.028

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.403
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.996
- **Median Q (composite search score)**: -0.045
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.380


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.74194,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.08214,"align_1.align_tolerance":0.00868,"approach_1.approach_height":0.1366,"approach_1.approach_speed":0.21616,"approach_1.approach_tolerance":0.02989,"insert_1.insertion_depth":0.07523,"insert_1.insertion_force_guard_threshold":40.83031,"insert_1.insertion_speed":0.04687},"optimized_scores":{"best_composite_score":-0.04524,"best_fitness_score":0.38476,"best_task_score":0.94161},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.51307,-0.01275,0.07763],"force_p95":1299.0106,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1326.95695,"mean_force":705.83219,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49592,-0.01296,0.08106]},{"body_a":"peg_socket","body_b":"link7","contact_count":909.0,"contact_point_centroid":[0.54072,-0.01691,0.07988],"force_p95":374.35662,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1057.05208,"mean_force":319.2529,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46979,-0.02093,0.13433]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.4503,-0.01016,0.07982],"force_p95":665.93707,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":700.98639,"mean_force":350.49319,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44768,-0.01354,0.0936]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54078,-0.01517,0.07997],"force_p95":549.99541,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":549.99541,"mean_force":549.99541,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.4787,-0.03724,0.14175]}],"total_contact_groups":4},"final_pose_error":0.13864,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.4786,-0.03707,0.1418],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1326.95695,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":86.0,"n_steps_budget":600.0,"object_pos_end":[0.49513,-0.01005,0.28366],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20396,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48694,-0.00999,0.2445],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.5152,-0.03209,0.12676],"object_pos_start":[0.49513,-0.01005,0.28366],"object_to_goal_dist_end":0.05872,"object_to_goal_dist_start":0.20396,"object_z_max":0.28366,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":923.0,"raw_peak_contact_force":1326.95695,"tcp_end":[0.47861,-0.03776,0.14188],"tcp_start":[0.48694,-0.00999,0.2445],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.51509,-0.03153,0.12638],"object_pos_start":[0.5152,-0.03209,0.12676],"object_to_goal_dist_end":0.05808,"object_to_goal_dist_start":0.05872,"object_z_max":0.12676,"peak_contact_force":549.99541,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":549.99541,"subtask_id":"insertion","tcp_end":[0.4786,-0.03707,0.1418],"tcp_start":[0.47861,-0.03776,0.14188],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.15909,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.11734,"align_1.align_tolerance":0.01153,"approach_1.approach_height":0.124,"approach_1.approach_speed":0.41084,"approach_1.approach_tolerance":0.02347,"insert_1.insertion_depth":0.1067,"insert_1.insertion_force_guard_threshold":35.77699,"insert_1.insertion_speed":0.04019},"optimized_scores":{"best_composite_score":-0.06394,"best_fitness_score":0.36606,"best_task_score":0.90935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.50125,-0.01974,0.07557],"force_p95":1381.56035,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1405.03586,"mean_force":545.22375,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48993,-0.01982,0.08121]},{"body_a":"peg_socket","body_b":"link7","contact_count":415.0,"contact_point_centroid":[0.5264,-0.02437,0.06708],"force_p95":413.1542,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1093.38904,"mean_force":340.1014,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46036,-0.02242,0.1218]},{"body_a":"world","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.67806,-0.02099,-9e-05],"force_p95":560.34932,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":659.77845,"mean_force":138.93649,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46275,-0.02342,0.12362]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67822,-0.02086,-9e-05],"force_p95":271.19311,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.19311,"mean_force":271.19311,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46319,-0.0287,0.1239]}],"total_contact_groups":4},"final_pose_error":0.15087,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46318,-0.02868,0.12393],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1405.03586,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":138.0,"n_steps_budget":600.0,"object_pos_end":[0.48397,-0.01557,0.26403],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18538,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47382,-0.01543,0.22534],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":516.0,"n_steps_budget":690.0,"object_pos_end":[0.50047,-0.0271,0.10949],"object_pos_start":[0.48397,-0.01557,0.26403],"object_to_goal_dist_end":0.04005,"object_to_goal_dist_start":0.18538,"object_z_max":0.26403,"peak_contact_force":188.22546,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":587.0,"raw_peak_contact_force":1405.03586,"tcp_end":[0.46319,-0.0287,0.1239],"tcp_start":[0.47382,-0.01543,0.22534],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50046,-0.02708,0.10952],"object_pos_start":[0.50047,-0.0271,0.10949],"object_to_goal_dist_end":0.04007,"object_to_goal_dist_start":0.04005,"object_z_max":0.10949,"peak_contact_force":271.19311,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":271.19311,"subtask_id":"insertion","tcp_end":[0.46318,-0.02868,0.12393],"tcp_start":[0.46319,-0.0287,0.1239],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.91228,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.06344,"align_1.align_tolerance":0.00519,"approach_1.approach_height":0.18081,"approach_1.approach_speed":0.24472,"approach_1.approach_tolerance":0.00963,"insert_1.insertion_depth":0.10184,"insert_1.insertion_force_guard_threshold":38.4783,"insert_1.insertion_speed":0.02296},"optimized_scores":{"best_composite_score":-0.02661,"best_fitness_score":0.40339,"best_task_score":0.99577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.56727,0.0008,0.0787],"force_p95":1271.22093,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1300.7633,"mean_force":797.06548,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55112,0.00077,0.08248]},{"body_a":"peg_socket","body_b":"link7","contact_count":877.0,"contact_point_centroid":[0.59518,-0.00321,0.07975],"force_p95":357.70834,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1235.95795,"mean_force":256.0879,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50506,-0.00032,0.11525]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.50137,0.00808,0.07844],"force_p95":899.07007,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":919.9629,"mean_force":295.42098,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4966,0.00027,0.08591]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5953,-0.00419,0.07991],"force_p95":281.97591,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.97591,"mean_force":281.97591,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51357,0.00197,0.12136]}],"total_contact_groups":4},"final_pose_error":0.14499,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.51362,0.00213,0.12149],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1300.7633,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":203.0,"n_steps_budget":600.0,"object_pos_end":[0.53031,0.0007,0.30309],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.22514,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52617,0.00069,0.2633],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55343,-0.00018,0.11871],"object_pos_start":[0.53031,0.0007,0.30309],"object_to_goal_dist_end":0.06598,"object_to_goal_dist_start":0.22514,"object_z_max":0.30309,"peak_contact_force":398.74545,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":907.0,"raw_peak_contact_force":1300.7633,"tcp_end":[0.51357,0.00197,0.12136],"tcp_start":[0.52617,0.00069,0.2633],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55348,-6e-05,0.11882],"object_pos_start":[0.55343,-0.00018,0.11871],"object_to_goal_dist_end":0.06608,"object_to_goal_dist_start":0.06598,"object_z_max":0.11871,"peak_contact_force":281.97591,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":281.97591,"subtask_id":"insertion","tcp_end":[0.51362,0.00213,0.12149],"tcp_start":[0.51357,0.00197,0.12136],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```