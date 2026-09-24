## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3475 | 0.20 | ❌ rejected |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3506 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.348) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
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
    - 0.04
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.348
- **task_score** (E): 0.200
- **fitness_score**: 0.244  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2522 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0583 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.140, 0.056) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 228.814 | 278.300 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, 0.140, 0.056)→(0.508, 0.140, 0.056) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 144.729 | 144.729 |
| push_1 | push | 0.00 / step_budget | (0.508, 0.140, 0.056)→(0.508, 0.082, 0.052) | (0.504, 0.095, 0.034)→(0.505, 0.050, 0.035) | 0.175→0.131 | 1.00 / 2.667 | 160.608 | 525.272 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.329
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.329
- phase_score: 0.277
- phase_breakdown.push_score: 0.039
- phase_breakdown.approach_score: 0.708
- phase_breakdown.contact_score: 0.558

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.298
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.329
- **Median Q (composite search score)**: 0.359
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.227


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1844,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05322,"contact_1.contact_force":11.12149,"contact_1.speed":0.03261,"push_1.push_speed":0.06407},"optimized_scores":{"best_composite_score":0.35879,"best_fitness_score":0.25545,"best_task_score":0.22662},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.52501,0.11978,0.06],"force_p95":643.86369,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":680.61963,"mean_force":250.887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51298,0.07864,0.05244]},{"body_a":"world","body_b":"link7","contact_count":374.0,"contact_point_centroid":[0.51304,0.18329,-2e-05],"force_p95":478.59455,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.46641,"mean_force":136.47719,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51513,0.12082,0.05337]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":103.0,"contact_point_centroid":[0.47495,0.11993,0.0527],"force_p95":266.9253,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.4167,"mean_force":145.60915,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51298,0.07864,0.05245]},{"body_a":"world","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.52178,0.20885,-0.00031],"force_p95":237.97771,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.74146,"mean_force":221.92297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51928,0.14788,0.05483]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":574.0,"contact_point_centroid":[0.52501,0.11731,0.05729],"force_p95":192.43458,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.4675,"mean_force":174.32804,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51409,0.11653,0.05286]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52224,0.20897,-9e-05],"force_p95":143.25953,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.25953,"mean_force":143.25953,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51905,0.14905,0.05636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.50382,0.08473,0.0098],"force_p95":2.24515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.56506,"mean_force":1.40794,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51463,0.11811,0.05315]},{"body_a":"attachment","body_b":"peg","contact_count":587.0,"contact_point_centroid":[0.50459,0.11765,0.04775],"force_p95":4.02698,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.23167,"mean_force":1.62728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51413,0.11821,0.05288]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52512,0.07543,0.03636],"force_p95":12.81483,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.66811,"mean_force":2.06862,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51266,0.09776,0.05231]},{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.50575,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55843,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50671,0.17556,0.17008]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50394,0.21891,0.2903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52151,0.09568,0.00939],"force_p95":0.54217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54217,"mean_force":0.54217,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51905,0.14905,0.05636]}],"total_contact_groups":12},"final_pose_error":0.15997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50547,0.03186,0.03738],"final_tcp_position":[0.5131,0.07894,0.05244],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":680.61963,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":221.25469,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1028.0,"raw_peak_contact_force":278.74146,"subtask_id":"approach","tcp_end":[0.51905,0.14905,0.05636],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.50595,0.10457,0.03384],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":143.25953,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":143.25953,"subtask_id":"contact","tcp_end":[0.51898,0.14898,0.05645],"tcp_start":[0.51905,0.14905,0.05636],"tcp_to_object_dist_end":0.05151,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.03186,0.03738],"object_pos_start":[0.50595,0.10457,0.03384],"object_to_goal_dist_end":0.11203,"object_to_goal_dist_start":0.18477,"object_z_max":0.04079,"peak_contact_force":1.41421,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2738.0,"raw_peak_contact_force":680.61963,"subtask_id":"push","tcp_end":[0.5131,0.07894,0.05244],"tcp_start":[0.51898,0.14898,0.05645],"tcp_to_object_dist_end":0.05002,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13208,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0441,"contact_1.contact_force":6.34186,"contact_1.speed":0.00979,"push_1.push_speed":0.06262},"optimized_scores":{"best_composite_score":0.28287,"best_fitness_score":0.17953,"best_task_score":0.04486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":624.0,"contact_point_centroid":[0.46918,0.11992,0.06],"force_p95":244.5352,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":393.33563,"mean_force":220.09234,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50175,0.08227,0.05223]},{"body_a":"world","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.50207,0.17429,-0.00033],"force_p95":267.16588,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.93766,"mean_force":245.3459,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.11312,0.05458]},{"body_a":"world","body_b":"link7","contact_count":352.0,"contact_point_centroid":[0.5007,0.15773,-2e-05],"force_p95":130.50853,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.38186,"mean_force":100.7446,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49943,0.09517,0.05358]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50245,0.1743,-0.0001],"force_p95":148.87348,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.87348,"mean_force":148.87348,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49958,0.1141,0.05607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":985.0,"contact_point_centroid":[0.50325,0.06225,0.0094],"force_p95":0.60126,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.83411,"mean_force":0.66567,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50081,0.08777,0.05278]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.50247,0.08334,0.05542],"force_p95":23.34477,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.45398,"mean_force":3.13815,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49991,0.08327,0.05311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49712,0.15948,0.17241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51448,0.05356,0.00938],"force_p95":0.54788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54788,"mean_force":0.54788,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49958,0.1141,0.05607]}],"total_contact_groups":8},"final_pose_error":0.16504,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50348,0.06028,0.03381],"final_tcp_position":[0.50329,0.08459,0.05169],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":393.33563,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":249.20943,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":293.93766,"subtask_id":"approach","tcp_end":[0.49958,0.1141,0.05607],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":148.87348,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":148.87348,"subtask_id":"contact","tcp_end":[0.49951,0.11404,0.05616],"tcp_start":[0.49958,0.1141,0.05607],"tcp_to_object_dist_end":0.05183,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50348,0.06028,0.03381],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14046,"object_to_goal_dist_start":0.14758,"object_z_max":0.03552,"peak_contact_force":248.45898,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1999.0,"raw_peak_contact_force":393.33563,"subtask_id":"push","tcp_end":[0.50329,0.08459,0.05169],"tcp_start":[0.49951,0.11404,0.05616],"tcp_to_object_dist_end":0.03017,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03853,"contact_1.contact_force":8.83476,"contact_1.speed":0.03456,"push_1.push_speed":0.05973},"optimized_scores":{"best_composite_score":0.40097,"best_fitness_score":0.29764,"best_task_score":0.32896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":149.0,"contact_point_centroid":[0.47497,0.11989,0.05971],"force_p95":419.66071,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":501.86013,"mean_force":243.6048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50591,0.08076,0.05235]},{"body_a":"world","body_b":"link7","contact_count":770.0,"contact_point_centroid":[0.5063,0.1772,-2e-05],"force_p95":161.59434,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.67465,"mean_force":116.99048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50457,0.11434,0.05329]},{"body_a":"world","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.50854,0.21548,-0.00032],"force_p95":233.78982,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.22105,"mean_force":216.80408,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50603,0.15447,0.05477]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50898,0.2156,-9e-05],"force_p95":142.05252,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.05252,"mean_force":142.05252,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50581,0.15562,0.05629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":911.0,"contact_point_centroid":[0.50322,0.08384,0.00955],"force_p95":2.46261,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.74396,"mean_force":1.0809,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50473,0.11212,0.05322]},{"body_a":"attachment","body_b":"peg","contact_count":257.0,"contact_point_centroid":[0.50447,0.1054,0.04984],"force_p95":10.73388,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.49875,"mean_force":2.10298,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50465,0.10524,0.05301]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":133.0,"contact_point_centroid":[0.52521,0.07708,0.04204],"force_p95":1.43934,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.05161,"mean_force":0.51515,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50496,0.09578,0.05288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.50356,0.11166,0.00939],"force_p95":0.60796,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55209,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50016,0.17917,0.17102]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51952,0.12,0.00939],"force_p95":0.58466,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58466,"mean_force":0.58466,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50581,0.15562,0.05629]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50379,0.20566,0.2996]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47481,0.08324,0.05863],"force_p95":0.301,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3465,"mean_force":0.09894,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50465,0.10313,0.05298]}],"total_contact_groups":11},"final_pose_error":0.16189,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50647,0.05914,0.03385],"final_tcp_position":[0.50635,0.08131,0.05212],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":501.86013,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11176,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":215.97728,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1013.0,"raw_peak_contact_force":262.22105,"subtask_id":"approach","tcp_end":[0.50581,0.15562,0.05629],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04931,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50378,0.11174,0.03383],"object_pos_start":[0.50376,0.11176,0.03383],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.1919,"object_z_max":0.03383,"peak_contact_force":142.05252,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":142.05252,"subtask_id":"contact","tcp_end":[0.50574,0.15555,0.05637],"tcp_start":[0.50581,0.15562,0.05629],"tcp_to_object_dist_end":0.0493,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,0.05914,0.03385],"object_pos_start":[0.50378,0.11174,0.03383],"object_to_goal_dist_end":0.13943,"object_to_goal_dist_start":0.19188,"object_z_max":0.03668,"peak_contact_force":231.9495,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2232.0,"raw_peak_contact_force":501.86013,"subtask_id":"push","tcp_end":[0.50635,0.08131,0.05212],"tcp_start":[0.50574,0.15555,0.05637],"tcp_to_object_dist_end":0.02873,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```