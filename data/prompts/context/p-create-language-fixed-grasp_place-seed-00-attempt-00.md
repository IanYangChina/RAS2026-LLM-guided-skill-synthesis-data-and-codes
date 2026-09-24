## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.1529 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.153) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: grasp_1
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: transport_arc
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.153
- **task_score** (E): 0.249
- **fitness_score**: 0.343  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.190

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0567 |
| descend_1 | 1.00 | 1.00 | 0.2221 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| transport_arc | 0.00 | 1.00 | 0.1002 |
| release_1 | 1.00 | 1.00 | 0.0255 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.001, 0.272) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.001, 0.272)→(0.493, 0.001, 0.050) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.050)→(0.485, 0.000, 0.041) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 41.000 | 0.144 | 0.186 |
| transport_arc | approach | 0.00 / step_budget | (0.485, 0.000, 0.041)→(0.512, 0.062, 0.112) | (0.497, 0.001, 0.026)→(0.522, 0.062, 0.086) | 0.266→0.174 | 1.00 / 20.667 | 0.113 | 0.426 |
| release_1 | release | 1.00 / step_budget | (0.512, 0.062, 0.112)→(0.506, 0.061, 0.137) | (0.522, 0.062, 0.086)→(0.526, 0.075, 0.015) | 0.174→0.213 | 1.00 / 4.000 | 0.116 | 1.149 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.344
- phase_score: 0.277
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.descend_1_score: 0.801
- phase_breakdown.transport_arc_score: 0.064
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.065
- grasp_place_fitness: 0.379

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.379
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.344
- **Median Q (composite search score)**: 0.136
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.813


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72277,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29982,"descend_1.grasp_z_offset":0.0101},"optimized_scores":{"best_composite_score":0.13401,"best_fitness_score":0.32401,"best_task_score":0.19903},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":268.0,"contact_point_centroid":[0.52303,0.0268,-0.00439],"force_p95":0.89263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1626,"mean_force":0.26811,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50619,0.02831,0.13468]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.51156,-0.0197,-0.00108],"force_p95":0.29685,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52248,"mean_force":0.13141,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49947,-0.02121,0.03752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14757.0,"contact_point_centroid":[0.50591,0.01904,0.07781],"force_p95":0.10538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29783,"mean_force":0.06737,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50336,0.00011,0.07603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16567.0,"contact_point_centroid":[0.50581,-0.01901,0.07662],"force_p95":0.09651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27613,"mean_force":0.06153,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50326,-0.00025,0.07538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.5163,0.00991,0.11979],"force_p95":0.11051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18144,"mean_force":0.07491,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51037,0.02863,0.11796]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51369,-0.02288,-0.00204],"force_p95":0.13522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16573,"mean_force":0.12612,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50194,-0.02262,0.03693]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":767.0,"contact_point_centroid":[0.51667,0.0472,0.11918],"force_p95":0.09724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16304,"mean_force":0.06657,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51043,0.02863,0.11802]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.5137,-0.02302,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50458,-0.01138,0.31015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4110.0,"contact_point_centroid":[0.50122,-0.00339,0.03842],"force_p95":0.07681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12316,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50077,-0.02259,0.03565]},{"body_a":"world","body_b":"grasp_target","contact_count":3324.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50856,-0.02168,0.1812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4894.0,"contact_point_centroid":[0.50129,-0.04167,0.03748],"force_p95":0.06901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08825,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50077,-0.02259,0.03565]}],"total_contact_groups":11},"final_pose_error":0.16504,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.52874,0.02682,0.01606],"final_tcp_position":[0.51217,0.02862,0.12029],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.1626,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50994,-0.02063,0.32088],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3324.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50897,-0.02279,0.0447],"tcp_start":[0.50994,-0.02063,0.32088],"tcp_to_object_dist_end":0.01927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.0225,0.02584],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26542,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13266,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.16573,"subtask_id":"grasp_1","tcp_end":[0.50074,-0.02259,0.03561],"tcp_start":[0.50897,-0.02279,0.0447],"tcp_to_object_dist_end":0.01614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52362,0.02869,0.09975],"object_pos_start":[0.51359,-0.0225,0.02584],"object_to_goal_dist_end":0.17605,"object_to_goal_dist_start":0.26542,"object_z_max":0.09968,"peak_contact_force":0.11144,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31496.0,"raw_peak_contact_force":0.52248,"subtask_id":"transport_arc","tcp_end":[0.51217,0.02862,0.12029],"tcp_start":[0.50074,-0.02259,0.03561],"tcp_to_object_dist_end":0.02352,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52874,0.02682,0.01606],"object_pos_start":[0.52362,0.02869,0.09975],"object_to_goal_dist_end":0.24214,"object_to_goal_dist_start":0.17605,"object_z_max":0.09976,"peak_contact_force":0.1134,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1699.0,"raw_peak_contact_force":1.1626,"subtask_id":"release_1","tcp_end":[0.50606,0.0283,0.14516],"tcp_start":[0.51217,0.02862,0.12029],"tcp_to_object_dist_end":0.13108,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88608,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15546,"descend_1.grasp_z_offset":0.02518},"optimized_scores":{"best_composite_score":0.18861,"best_fitness_score":0.37861,"best_task_score":0.34448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":187.0,"contact_point_centroid":[0.51614,0.16952,-0.00417],"force_p95":1.00674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21226,"mean_force":0.30501,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50817,0.12105,0.12523]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.5028,0.05002,-0.00119],"force_p95":0.26847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32728,"mean_force":0.17004,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48797,0.04775,0.05368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12069.0,"contact_point_centroid":[0.49987,0.05975,0.07577],"force_p95":0.1249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29143,"mean_force":0.0819,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49766,0.07807,0.0779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":850.0,"contact_point_centroid":[0.51794,0.14275,0.10058],"force_p95":0.17728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2722,"mean_force":0.13109,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5113,0.12183,0.10554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9957.0,"contact_point_centroid":[0.50189,0.0981,0.07607],"force_p95":0.13217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2385,"mean_force":0.09486,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49839,0.07976,0.07914]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04492,-0.00215],"force_p95":0.1652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21502,"mean_force":0.13374,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48978,0.04351,0.05253]},{"body_a":"world","body_b":"grasp_target","contact_count":1420.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49801,0.01913,0.24666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3276.0,"contact_point_centroid":[0.49105,0.02441,0.0505],"force_p95":0.10751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12803,"mean_force":0.06377,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48866,0.04341,0.0513]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49589,0.04175,0.12601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":518.0,"contact_point_centroid":[0.51844,0.10403,0.10168],"force_p95":0.12067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12198,"mean_force":0.08216,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51257,0.12216,0.10604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4858.0,"contact_point_centroid":[0.48915,0.06215,0.05136],"force_p95":0.08146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08447,"mean_force":0.0451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48866,0.04341,0.05131]}],"total_contact_groups":11},"final_pose_error":0.13771,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52044,0.16648,0.01458],"final_tcp_position":[0.51436,0.12245,0.10842],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.21226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49773,0.03961,0.19311],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49652,0.04411,0.06],"tcp_start":[0.49773,0.03961,0.19311],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04372,0.02538],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24331,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16511,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9934.0,"raw_peak_contact_force":0.21502,"subtask_id":"grasp_1","tcp_end":[0.48863,0.04341,0.05127],"tcp_start":[0.49652,0.04411,0.06],"tcp_to_object_dist_end":0.02877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5206,0.12213,0.07145],"object_pos_start":[0.50116,0.04372,0.02538],"object_to_goal_dist_end":0.15052,"object_to_goal_dist_start":0.24331,"object_z_max":0.07142,"peak_contact_force":0.1153,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22350.0,"raw_peak_contact_force":0.32728,"subtask_id":"transport_arc","tcp_end":[0.51436,0.12245,0.10842],"tcp_start":[0.48863,0.04341,0.05127],"tcp_to_object_dist_end":0.0375,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52044,0.16648,0.01458],"object_pos_start":[0.5206,0.12213,0.07145],"object_to_goal_dist_end":0.15986,"object_to_goal_dist_start":0.15052,"object_z_max":0.07145,"peak_contact_force":0.11626,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1555.0,"raw_peak_contact_force":1.21226,"subtask_id":"release_1","tcp_end":[0.50808,0.12104,0.13279],"tcp_start":[0.51436,0.12245,0.10842],"tcp_to_object_dist_end":0.12725,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70408,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27922,"descend_1.grasp_z_offset":0.01007},"optimized_scores":{"best_composite_score":0.13612,"best_fitness_score":0.32612,"best_task_score":0.20397},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":268.0,"contact_point_centroid":[0.52098,0.03199,-0.00424],"force_p95":0.81848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07245,"mean_force":0.26494,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50401,0.03339,0.12268]},{"body_a":"world","body_b":"grasp_target","contact_count":226.0,"contact_point_centroid":[0.47814,-0.01634,-0.00109],"force_p95":0.25422,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42719,"mean_force":0.14773,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46436,-0.01753,0.03929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14942.0,"contact_point_centroid":[0.48563,0.0241,0.07385],"force_p95":0.10464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23291,"mean_force":0.06593,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48332,0.00514,0.0719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16866.0,"contact_point_centroid":[0.4853,-0.01397,0.07288],"force_p95":0.09584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22189,"mean_force":0.06049,"phase_index":3.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48303,0.00485,0.07149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":758.0,"contact_point_centroid":[0.51449,0.05232,0.10763],"force_p95":0.09735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20158,"mean_force":0.06718,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50834,0.03376,0.10632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":678.0,"contact_point_centroid":[0.51411,0.01502,0.10804],"force_p95":0.11051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19848,"mean_force":0.07356,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50824,0.03375,0.10623]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00205],"force_p95":0.1372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17784,"mean_force":0.12656,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46545,-0.01962,0.03837]},{"body_a":"world","body_b":"grasp_target","contact_count":512.0,"contact_point_centroid":[0.47616,-0.02015,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12358,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48954,-0.00726,0.30025]},{"body_a":"world","body_b":"grasp_target","contact_count":3192.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47511,-0.01727,0.172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.46436,-0.00038,0.0396],"force_p95":0.06768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09756,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46435,-0.0196,0.03727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5150.0,"contact_point_centroid":[0.46422,-0.03882,0.03914],"force_p95":0.06638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08412,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46435,-0.0196,0.03727]}],"total_contact_groups":11},"final_pose_error":0.19257,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52958,0.03206,0.01585],"final_tcp_position":[0.5101,0.03378,0.10857],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.1226,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":512.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48008,-0.01481,0.30191],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3192.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47209,-0.01977,0.04507],"tcp_start":[0.48008,-0.01481,0.30191],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01969,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13538,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11785.0,"raw_peak_contact_force":0.17784,"subtask_id":"grasp_1","tcp_end":[0.46432,-0.0196,0.03724],"tcp_start":[0.47209,-0.01977,0.04507],"tcp_to_object_dist_end":0.01638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52164,0.03379,0.08742],"object_pos_start":[0.47606,-0.01969,0.02582],"object_to_goal_dist_end":0.19571,"object_to_goal_dist_start":0.28826,"object_z_max":0.08737,"peak_contact_force":0.11139,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32034.0,"raw_peak_contact_force":0.42719,"subtask_id":"transport_arc","tcp_end":[0.5101,0.03378,0.10857],"tcp_start":[0.46432,-0.0196,0.03724],"tcp_to_object_dist_end":0.02409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52958,0.03206,0.01585],"object_pos_start":[0.52164,0.03379,0.08742],"object_to_goal_dist_end":0.23847,"object_to_goal_dist_start":0.19571,"object_z_max":0.08743,"peak_contact_force":0.11791,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1704.0,"raw_peak_contact_force":1.07245,"subtask_id":"release_1","tcp_end":[0.50386,0.03338,0.13355],"tcp_start":[0.5101,0.03378,0.10857],"tcp_to_object_dist_end":0.12048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```