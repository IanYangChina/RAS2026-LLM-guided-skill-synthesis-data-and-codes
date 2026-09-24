## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5600 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6573 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.560) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
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
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.05
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_arc
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
    - 0.15
    tolerance: 0.02
  parameters:
    transport_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: place_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.560
- **task_score** (E): 1.000
- **fitness_score**: 0.880  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0795 |
| descend_1 | 1.00 | 1.00 | 0.1722 |
| grasp_1 | 1.00 | 1.00 | 0.0136 |
| lift_1 | 1.00 | 1.00 | 0.0955 |
| transport_arc | 1.00 | 1.00 | 0.3183 |
| place_1 | 1.00 | 1.00 | 0.1849 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.003, 0.227) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.003, 0.227)→(0.493, 0.001, 0.055) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.055)→(0.484, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.025) | 0.265→0.266 | 1.00 / 46.333 | 0.169 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.045)→(0.490, 0.000, 0.140) | (0.497, 0.001, 0.025)→(0.504, 0.000, 0.121) | 0.266→0.219 | 1.00 / 42.333 | 0.090 | 0.419 |
| transport_arc | approach | 1.00 / step_budget | (0.490, 0.000, 0.140)→(0.576, 0.172, 0.390) | (0.504, 0.000, 0.121)→(0.592, 0.177, 0.369) | 0.219→0.183 | 1.00 / 34.333 | 95.667 | 0.343 |
| place_1 | descend | 1.00 / step_budget | (0.576, 0.172, 0.390)→(0.580, 0.183, 0.205) | (0.592, 0.177, 0.369)→(0.586, 0.186, 0.177) | 0.183→0.010 | 1.00 / 28.667 | 0.095 | 0.329 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.496
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.350
- phase_breakdown.release_1_score: 0.671
- phase_breakdown.transport_arc_score: 0.020
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.866
- phase_breakdown.approach_1_score: 0.045
- grasp_place_fitness: 0.964

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.964
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.643
- **K-run variance**: 0.0139
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.387


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92754,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13829,"descend_1.grasp_z_offset":0.00508,"lift_1.lift_height":0.21993,"transport_arc.transport_z_offset":0.22254},"optimized_scores":{"best_composite_score":0.64358,"best_fitness_score":0.96358,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51113,-0.02142,-0.00167],"force_p95":0.40978,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47945,"mean_force":0.19869,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49843,-0.02095,0.0455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3979.0,"contact_point_centroid":[0.54995,0.1624,0.3334],"force_p95":0.11606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3356,"mean_force":0.08229,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55026,0.14325,0.3327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3683.0,"contact_point_centroid":[0.50202,-0.04049,0.11706],"force_p95":0.09438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30154,"mean_force":0.05858,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50227,-0.02128,0.1133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3910.0,"contact_point_centroid":[0.50364,-0.00214,0.11724],"force_p95":0.09338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29363,"mean_force":0.05646,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50246,-0.02129,0.11539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4624.0,"contact_point_centroid":[0.55814,0.12606,0.33159],"force_p95":0.10802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29196,"mean_force":0.07374,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55026,0.14331,0.33179]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51378,-0.02301,-0.00218],"force_p95":0.17075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22554,"mean_force":0.13548,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50086,-0.02099,0.04563]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10014.0,"contact_point_centroid":[0.53141,0.03811,0.30595],"force_p95":0.09556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16662,"mean_force":0.0588,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52813,0.05686,0.30373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5527.0,"contact_point_centroid":[0.50062,-0.00175,0.04646],"force_p95":0.06733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14876,"mean_force":0.03986,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49967,-0.02096,0.04434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10262.0,"contact_point_centroid":[0.527,0.07265,0.30109],"force_p95":0.0933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14401,"mean_force":0.0563,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52728,0.05364,0.29921]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.5137,-0.02302,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50346,-0.00083,0.24281]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50783,-0.01699,0.12074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5266.0,"contact_point_centroid":[0.49949,-0.04027,0.04856],"force_p95":0.06475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07537,"mean_force":0.04235,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49967,-0.02096,0.04434]}],"total_contact_groups":12},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55894,0.15194,0.21316],"final_tcp_position":[0.55103,0.14909,0.24151],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":286.83354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":912.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50827,-0.01301,0.18443],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":832.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50883,-0.02105,0.05494],"tcp_start":[0.50827,-0.01301,0.18443],"tcp_to_object_dist_end":0.0294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51373,-0.02192,0.02537],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26536,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1679,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12593.0,"raw_peak_contact_force":0.22554,"subtask_id":"grasp_1","tcp_end":[0.49964,-0.02096,0.0443],"tcp_start":[0.50883,-0.02105,0.05494],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.52559,-0.02278,0.17824],"object_pos_start":[0.51373,-0.02192,0.02537],"object_to_goal_dist_end":0.18208,"object_to_goal_dist_start":0.26536,"object_z_max":0.17735,"peak_contact_force":0.08144,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7658.0,"raw_peak_contact_force":0.47945,"tcp_end":[0.5092,-0.02169,0.1964],"tcp_start":[0.49964,-0.02096,0.0443],"tcp_to_object_dist_end":0.02448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.56732,0.14186,0.39783],"object_pos_start":[0.52559,-0.02278,0.17824],"object_to_goal_dist_end":0.17661,"object_to_goal_dist_start":0.18208,"object_z_max":0.39745,"peak_contact_force":286.83354,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20276.0,"raw_peak_contact_force":0.16662,"subtask_id":"transport_arc","tcp_end":[0.54995,0.13787,0.41827],"tcp_start":[0.5092,-0.02169,0.1964],"tcp_to_object_dist_end":0.02712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.55894,0.15194,0.21316],"object_pos_start":[0.56732,0.14186,0.39783],"object_to_goal_dist_end":0.01007,"object_to_goal_dist_start":0.17661,"object_z_max":0.39816,"peak_contact_force":0.09676,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8603.0,"raw_peak_contact_force":0.3356,"subtask_id":"release_1","tcp_end":[0.55103,0.14909,0.24151],"tcp_start":[0.54995,0.13787,0.41827],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78218,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22667,"descend_1.grasp_z_offset":0.00507,"lift_1.lift_height":0.06428,"transport_arc.transport_z_offset":0.2042},"optimized_scores":{"best_composite_score":0.39339,"best_fitness_score":0.71339,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.491,0.02472,-0.00018],"force_p95":0.63991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64979,"mean_force":0.45258,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4879,0.04217,0.0498]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50059,0.04386,-0.00183],"force_p95":0.29197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33991,"mean_force":0.10601,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48759,0.04217,0.0457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13784.0,"contact_point_centroid":[0.51717,0.1546,0.18794],"force_p95":0.07835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31138,"mean_force":0.0518,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52089,0.13599,0.18427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14298.0,"contact_point_centroid":[0.52458,0.11621,0.18337],"force_p95":0.08166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30859,"mean_force":0.05068,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52046,0.13488,0.18263]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.55345,0.25442,0.25245],"force_p95":0.10106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28743,"mean_force":0.05935,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55871,0.23621,0.24991]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5013,0.04501,-0.00224],"force_p95":0.18583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2361,"mean_force":0.13959,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48923,0.04233,0.04609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.56605,0.21872,0.24777],"force_p95":0.09968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19996,"mean_force":0.05868,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55873,0.23628,0.24873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.48681,0.06126,0.04965],"force_p95":0.13974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19911,"mean_force":0.07364,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48759,0.04217,0.04584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.48931,0.02305,0.04668],"force_p95":0.13694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18512,"mean_force":0.07539,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48758,0.04217,0.04586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4776.0,"contact_point_centroid":[0.49018,0.02309,0.0457],"force_p95":0.08179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16781,"mean_force":0.04592,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48806,0.04222,0.04484]},{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.50118,0.04505,-0.00168],"force_p95":0.13822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12396,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,0.01495,0.287]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49725,0.03688,0.16352]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5259.0,"contact_point_centroid":[0.48714,0.06145,0.04872],"force_p95":0.06987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08104,"mean_force":0.04267,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48806,0.04222,0.04485]}],"total_contact_groups":13},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56783,0.24727,0.13929],"final_tcp_position":[0.56033,0.24158,0.16584],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.64979,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02601],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24189,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49879,0.03098,0.27007],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02601],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24189,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49709,0.04297,0.05508],"tcp_start":[0.49879,0.03098,0.27007],"tcp_to_object_dist_end":0.02942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50133,0.04351,0.02518],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24354,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.18121,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11835.0,"raw_peak_contact_force":0.2361,"subtask_id":"grasp_1","tcp_end":[0.48803,0.04222,0.04481],"tcp_start":[0.49709,0.04297,0.05508],"tcp_to_object_dist_end":0.02375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49981,0.04339,0.03044],"object_pos_start":[0.50133,0.04351,0.02518],"object_to_goal_dist_end":0.24146,"object_to_goal_dist_start":0.24354,"object_z_max":0.02983,"peak_contact_force":0.11282,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":908.0,"raw_peak_contact_force":0.33991,"tcp_end":[0.48773,0.04216,0.04948],"tcp_start":[0.48803,0.04222,0.04481],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.57246,0.2385,0.30446],"object_pos_start":[0.49981,0.04339,0.03044],"object_to_goal_dist_end":0.15802,"object_to_goal_dist_start":0.24146,"object_z_max":0.30409,"peak_contact_force":0.08145,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28086.0,"raw_peak_contact_force":0.64979,"subtask_id":"transport_arc","tcp_end":[0.55819,0.23176,0.32505],"tcp_start":[0.48773,0.04216,0.04948],"tcp_to_object_dist_end":0.02595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.56783,0.24727,0.13929],"object_pos_start":[0.57246,0.2385,0.30446],"object_to_goal_dist_end":0.00856,"object_to_goal_dist_start":0.15802,"object_z_max":0.30479,"peak_contact_force":0.08912,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10490.0,"raw_peak_contact_force":0.28743,"subtask_id":"release_1","tcp_end":[0.56033,0.24158,0.16584],"tcp_start":[0.55819,0.23176,0.32505],"tcp_to_object_dist_end":0.02816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93274,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18001,"descend_1.grasp_z_offset":0.00531,"lift_1.lift_height":0.1992,"transport_arc.transport_z_offset":0.2624},"optimized_scores":{"best_composite_score":0.64316,"best_fitness_score":0.96316,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.47301,-0.0188,-0.00165],"force_p95":0.39062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43715,"mean_force":0.21832,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46303,-0.01852,0.04727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5433.0,"contact_point_centroid":[0.62007,0.17027,0.33119],"force_p95":0.10873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36544,"mean_force":0.07045,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62356,0.15173,0.33148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3020.0,"contact_point_centroid":[0.46537,-0.038,0.10797],"force_p95":0.11591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29039,"mean_force":0.06142,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46594,-0.01879,0.10529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6091.0,"contact_point_centroid":[0.62841,0.13384,0.32369],"force_p95":0.10735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28583,"mean_force":0.06499,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62375,0.152,0.32499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3328.0,"contact_point_centroid":[0.46694,0.00036,0.10741],"force_p95":0.11634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2731,"mean_force":0.05725,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46604,-0.01879,0.10631]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47621,-0.02016,-0.00214],"force_p95":0.16003,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21486,"mean_force":0.1327,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.01855,0.04733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13249.0,"contact_point_centroid":[0.54732,0.04489,0.30051],"force_p95":0.08711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21122,"mean_force":0.0556,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54475,0.06383,0.29871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13461.0,"contact_point_centroid":[0.54248,0.08175,0.29837],"force_p95":0.084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20881,"mean_force":0.05465,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54377,0.06273,0.29706]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.47616,-0.02015,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12346,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48977,-0.00181,0.26465]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4755,-0.01436,0.14237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.46528,0.00065,0.04752],"force_p95":0.0683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12039,"mean_force":0.04048,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01853,0.04619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.46416,-0.03782,0.04904],"force_p95":0.07129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0751,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46416,-0.01853,0.0462]}],"total_contact_groups":12},"final_pose_error":0.01946,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.6315,0.15943,0.1784],"final_tcp_position":[0.62733,0.15708,0.20892],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.43715,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":584.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47937,-0.01021,0.22694],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47299,-0.01861,0.0556],"tcp_start":[0.47937,-0.01021,0.22694],"tcp_to_object_dist_end":0.02979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47615,-0.01933,0.02551],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15809,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12208.0,"raw_peak_contact_force":0.21486,"subtask_id":"grasp_1","tcp_end":[0.46413,-0.01853,0.04616],"tcp_start":[0.47299,-0.01861,0.0556],"tcp_to_object_dist_end":0.02391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.48564,-0.01999,0.15569],"object_pos_start":[0.47615,-0.01933,0.02551],"object_to_goal_dist_end":0.23353,"object_to_goal_dist_start":0.28817,"object_z_max":0.15478,"peak_contact_force":0.0766,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6408.0,"raw_peak_contact_force":0.43715,"tcp_end":[0.47171,-0.01911,0.17539],"tcp_start":[0.46413,-0.01853,0.04616],"tcp_to_object_dist_end":0.02415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.63735,0.1515,0.40445],"object_pos_start":[0.48564,-0.01999,0.15569],"object_to_goal_dist_end":0.21466,"object_to_goal_dist_start":0.23353,"object_z_max":0.40414,"peak_contact_force":0.08742,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26710.0,"raw_peak_contact_force":0.21122,"subtask_id":"transport_arc","tcp_end":[0.62102,0.14773,0.42677],"tcp_start":[0.47171,-0.01911,0.17539],"tcp_to_object_dist_end":0.02792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.6315,0.15943,0.1784],"object_pos_start":[0.63735,0.1515,0.40445],"object_to_goal_dist_end":0.01162,"object_to_goal_dist_start":0.21466,"object_z_max":0.40471,"peak_contact_force":0.0979,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11524.0,"raw_peak_contact_force":0.36544,"subtask_id":"release_1","tcp_end":[0.62733,0.15708,0.20892],"tcp_start":[0.62102,0.14773,0.42677],"tcp_to_object_dist_end":0.0309,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```