## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1141 | 0.14 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0183 | 0.00 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 3 | -0.0544 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.114) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: reach_approach
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_duration:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_to_goal
- id: retract_away
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_away** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.114
- **task_score** (E): 0.141
- **fitness_score**: 0.216  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2554 |
| push_channel | 0.33 | 1.00 | 0.0254 |
| retract_away | 1.00 | 1.00 | 0.2178 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.121, 0.058) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.544 | 2.488 |
| push_channel | push | 0.33 / guard_failure | (0.509, 0.121, 0.058)→(0.506, 0.096, 0.054) | (0.504, 0.095, 0.034)→(0.504, 0.078, 0.037) | 0.175→0.158 | 1.00 / 3.000 | 19.750 | 41.634 |
| retract_away | retract | 1.00 / step_budget | (0.506, 0.096, 0.054)→(0.501, 0.183, 0.254) | (0.504, 0.078, 0.037)→(0.503, 0.068, 0.030) | 0.158→0.148 | 1.00 / 1.000 | 0.559 | 119.209 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.460
- alignment_error: None
- force_efficiency: 0.414
- terminal_score: 0.380
- phase_score: 0.357
- phase_breakdown.push_to_goal_score: 0.222
- phase_breakdown.reach_approach_score: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.366
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.380
- **Median Q (composite search score)**: -0.177
- **K-run variance**: 0.0114
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.334


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58475,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06113,"approach_behind.approach_tol":0.02399,"push_channel.push_duration":6.97903,"push_channel.push_speed":0.04032,"retract_away.retract_speed":0.28835,"retract_away.retract_tol":0.0611},"optimized_scores":{"best_composite_score":-0.2014,"best_fitness_score":0.1286,"best_task_score":0.0041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.51805,0.18188,-2e-05],"force_p95":214.05796,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.01108,"mean_force":133.47988,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51687,0.11989,0.05432]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,0.11995,0.0456],"force_p95":176.47668,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":183.45574,"mean_force":141.91367,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51685,0.11993,0.05436]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.11997,0.04559],"force_p95":51.45692,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.08125,"mean_force":45.83788,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51688,0.11998,0.05434]},{"body_a":"world","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.5182,0.1848,-1e-05],"force_p95":36.49931,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.14104,"mean_force":31.22227,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51697,0.12286,0.05438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":129.0,"contact_point_centroid":[0.50609,0.0986,0.0095],"force_p95":7.56168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.47733,"mean_force":1.72597,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51719,0.12392,0.05471]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50668,0.1212,0.04811],"force_p95":9.13136,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.24715,"mean_force":3.81531,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51691,0.12125,0.05436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50556,0.10461,0.00937],"force_p95":0.57728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56779,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50406,0.17189,0.17777]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50391,0.21872,0.28998]},{"body_a":"peg","body_b":"channel_base_body","contact_count":216.0,"contact_point_centroid":[0.50594,0.10292,0.00946],"force_p95":0.66903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83967,"mean_force":0.54421,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50949,0.15176,0.1489]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.507,0.11984,0.04751],"force_p95":0.13666,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13893,"mean_force":0.11624,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51687,0.11989,0.05432]}],"total_contact_groups":10},"final_pose_error":0.04991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,0.10335,0.0338],"final_tcp_position":[0.50345,0.18622,0.25215],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":223.01108,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54353,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":559.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51939,0.12988,0.05822],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.5058,0.10241,0.03559],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18256,"object_to_goal_dist_start":0.18492,"object_z_max":0.03558,"peak_contact_force":52.08125,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":242.0,"raw_peak_contact_force":52.08125,"subtask_id":"push_to_goal","tcp_end":[0.51688,0.1199,0.05433],"tcp_start":[0.51939,0.12988,0.05822],"tcp_to_object_dist_end":0.02792,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.5059,0.10335,0.0338],"object_pos_start":[0.5058,0.10241,0.03559],"object_to_goal_dist_end":0.18355,"object_to_goal_dist_start":0.18256,"object_z_max":0.03562,"peak_contact_force":0.54605,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":224.0,"raw_peak_contact_force":223.01108,"tcp_end":[0.50345,0.18622,0.25215],"tcp_start":[0.51688,0.1199,0.05433],"tcp_to_object_dist_end":0.23357,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11712,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.15728,"approach_behind.approach_tol":0.02855,"push_channel.push_duration":6.23816,"push_channel.push_speed":0.01283,"retract_away.retract_speed":0.09857,"retract_away.retract_tol":0.09974},"optimized_scores":{"best_composite_score":-0.17703,"best_fitness_score":0.15297,"best_task_score":0.03914},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11994,0.03406],"force_p95":105.27329,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.33919,"mean_force":65.64491,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49773,0.07988,0.05423]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49889,0.14196,-1e-05],"force_p95":53.40597,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.61351,"mean_force":25.01488,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49774,0.07987,0.05422]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11997,0.03409],"force_p95":45.8984,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.4071,"mean_force":41.32013,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49775,0.07994,0.05423]},{"body_a":"world","body_b":"link7","contact_count":212.0,"contact_point_centroid":[0.499,0.14812,-1e-05],"force_p95":34.36464,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.50159,"mean_force":30.18071,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49779,0.08606,0.05426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.50357,0.0618,0.00956],"force_p95":4.21854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.90375,"mean_force":1.0521,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4979,0.08684,0.05439]},{"body_a":"attachment","body_b":"peg","contact_count":89.0,"contact_point_centroid":[0.50271,0.08279,0.04336],"force_p95":6.17739,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.60951,"mean_force":1.97165,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49776,0.0828,0.05423]},{"body_a":"peg","body_b":"channel_base_body","contact_count":474.0,"contact_point_centroid":[0.50308,0.06741,0.00933],"force_p95":0.56189,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5648,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49481,0.15585,0.17196]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50289,0.06113,0.00942],"force_p95":0.60168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70969,"mean_force":0.54997,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49813,0.12823,0.1502]}],"total_contact_groups":8},"final_pose_error":0.04968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5028,0.0612,0.03379],"final_tcp_position":[0.49993,0.18025,0.25442],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":105.33919,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54753,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":474.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.50014,0.0959,0.0578],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.50287,0.06172,0.035],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14184,"object_to_goal_dist_start":0.14761,"object_z_max":0.03508,"peak_contact_force":1.11923,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":607.0,"raw_peak_contact_force":46.4071,"subtask_id":"push_to_goal","tcp_end":[0.49775,0.07988,0.05422],"tcp_start":[0.50014,0.0959,0.0578],"tcp_to_object_dist_end":0.02694,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.5028,0.0612,0.03379],"object_pos_start":[0.50287,0.06172,0.035],"object_to_goal_dist_end":0.14136,"object_to_goal_dist_start":0.14184,"object_z_max":0.035,"peak_contact_force":0.55097,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":257.0,"raw_peak_contact_force":105.33919,"tcp_end":[0.49993,0.18025,0.25442],"tcp_start":[0.49775,0.07988,0.05422],"tcp_to_object_dist_end":0.25071,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76522,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.12745,"approach_behind.approach_tol":0.02703,"push_channel.push_duration":8.16543,"push_channel.push_speed":0.0251,"retract_away.retract_speed":0.17506,"retract_away.retract_tol":0.07054},"optimized_scores":{"best_composite_score":0.03626,"best_fitness_score":0.36626,"best_task_score":0.38003},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50461,0.15011,-1e-05],"force_p95":29.27777,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.27777,"mean_force":29.27777,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50342,0.08823,0.05446]},{"body_a":"world","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.50468,0.17309,-0.0],"force_p95":20.57022,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.41313,"mean_force":16.84355,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50349,0.1112,0.05447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50371,0.08178,0.00992],"force_p95":5.56694,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.99323,"mean_force":2.97673,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50354,0.11079,0.05454]},{"body_a":"attachment","body_b":"peg","contact_count":927.0,"contact_point_centroid":[0.50362,0.10912,0.04249],"force_p95":5.27583,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.69669,"mean_force":2.79366,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50348,0.10915,0.05447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.49921,0.05894,0.0096],"force_p95":1.018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.68167,"mean_force":0.57249,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50137,0.13245,0.14872]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50354,0.08819,0.04257],"force_p95":4.69229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.20701,"mean_force":2.10761,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50337,0.0882,0.05451]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50354,0.1117,0.00936],"force_p95":0.62201,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56215,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49767,0.17456,0.17072]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47482,0.04995,0.05699],"force_p95":0.50962,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66801,"mean_force":0.14438,"phase_index":2.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50144,0.11499,0.1111]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50374,0.20561,0.29955]}],"total_contact_groups":9},"final_pose_error":0.04951,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50118,0.03813,0.02364],"final_tcp_position":[0.50099,0.18153,0.25407],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":29.27777,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11178,0.03377],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54008,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":470.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_approach","tcp_end":[0.50639,0.13649,0.05892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.06929,0.04037],"object_pos_start":[0.50368,0.11178,0.03377],"object_to_goal_dist_end":0.14934,"object_to_goal_dist_start":0.19191,"object_z_max":0.04036,"peak_contact_force":6.04906,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2373.0,"raw_peak_contact_force":26.41313,"subtask_id":"push_to_goal","tcp_end":[0.50343,0.08827,0.05448],"tcp_start":[0.50639,0.13649,0.05892],"tcp_to_object_dist_end":0.02365,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":960.0,"object_pos_end":[0.50118,0.03813,0.02364],"object_pos_start":[0.50369,0.06929,0.04037],"object_to_goal_dist_end":0.11927,"object_to_goal_dist_start":0.14934,"object_z_max":0.04079,"peak_contact_force":0.58114,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":265.0,"raw_peak_contact_force":29.27777,"tcp_end":[0.50099,0.18153,0.25407],"tcp_start":[0.50343,0.08827,0.05448],"tcp_to_object_dist_end":0.27142,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```