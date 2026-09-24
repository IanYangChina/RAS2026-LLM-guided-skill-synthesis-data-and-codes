## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6573 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3238 | 0.34 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2704 | 0.17 | ✅ accepted |

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

## Current Skill (Q=0.657) — your mutation base

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

- **Composite score**: 0.657
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0505 |
| descend_1 | 1.00 | 1.00 | 0.2179 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.1283 |
| transport_arc | 1.00 | 1.00 | 0.2690 |
| place_1 | 1.00 | 1.00 | 0.1171 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.005, 0.257) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 9.600 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.005, 0.257)→(0.492, 0.001, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.126 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.040)→(0.484, 0.001, 0.031) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 43.000 | 0.152 | 0.211 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.031)→(0.492, 0.001, 0.159) | (0.497, 0.001, 0.026)→(0.506, 0.000, 0.154) | 0.266→0.215 | 1.00 / 38.667 | 0.084 | 0.645 |
| transport_arc | approach | 1.00 / step_budget | (0.492, 0.001, 0.159)→(0.572, 0.169, 0.321) | (0.506, 0.000, 0.154)→(0.586, 0.173, 0.310) | 0.215→0.125 | 1.00 / 38.333 | 0.092 | 0.145 |
| place_1 | descend | 1.00 / step_budget | (0.572, 0.169, 0.321)→(0.578, 0.180, 0.204) | (0.586, 0.173, 0.310)→(0.590, 0.184, 0.190) | 0.125→0.008 | 1.00 / 31.000 | 0.099 | 0.219 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.789
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.342
- phase_breakdown.release_1_score: 0.673
- phase_breakdown.transport_arc_score: 0.018
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.811
- phase_breakdown.approach_1_score: 0.005
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.657
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92228,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17813,"descend_1.grasp_z_offset":0.005,"lift_1.lift_height":0.14847,"transport_arc.transport_z_offset":0.1842},"optimized_scores":{"best_composite_score":0.65695,"best_fitness_score":0.97695,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.51031,-0.02243,-0.00157],"force_p95":0.56456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66364,"mean_force":0.29696,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4986,-0.02204,0.03094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2039.0,"contact_point_centroid":[0.50024,-0.0414,0.07404],"force_p95":0.1408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.327,"mean_force":0.06802,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50108,-0.02217,0.07141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2488.0,"contact_point_centroid":[0.50215,-0.00315,0.07364],"force_p95":0.12504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32009,"mean_force":0.05825,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50116,-0.02217,0.07197]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02302,-0.00209],"force_p95":0.14863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20548,"mean_force":0.12932,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50099,-0.02208,0.03126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4004.0,"contact_point_centroid":[0.54771,0.16401,0.31851],"force_p95":0.09127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14166,"mean_force":0.06493,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55021,0.14521,0.31645]},{"body_a":"world","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.5137,-0.02302,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12342,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50344,-0.00295,0.26267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4178.0,"contact_point_centroid":[0.55669,0.12736,0.31703],"force_p95":0.08963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13598,"mean_force":0.06288,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55022,0.14522,0.31622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.50069,-0.003,0.03184],"force_p95":0.0651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12803,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49974,-0.02206,0.02991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17584.0,"contact_point_centroid":[0.53084,0.04464,0.26052],"force_p95":0.08108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12779,"mean_force":0.05783,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52787,0.0635,0.25829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19447.0,"contact_point_centroid":[0.52535,0.07717,0.25213],"force_p95":0.07816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12546,"mean_force":0.05305,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5264,0.05823,0.24987]},{"body_a":"world","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50685,-0.01746,0.13024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4201.0,"contact_point_centroid":[0.4991,-0.04134,0.03276],"force_p95":0.0787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08154,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49975,-0.02206,0.02992]}],"total_contact_groups":12},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56126,0.15258,0.22501],"final_tcp_position":[0.55094,0.14934,0.24112],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.66364,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":616.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50786,-0.01275,0.22372],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50842,-0.02219,0.03937],"tcp_start":[0.50786,-0.01275,0.22372],"tcp_to_object_dist_end":0.01438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02255,0.02569],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26555,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14738,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11288.0,"raw_peak_contact_force":0.20548,"subtask_id":"grasp_1","tcp_end":[0.49971,-0.02206,0.02988],"tcp_start":[0.50842,-0.02219,0.03937],"tcp_to_object_dist_end":0.01451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":117.0,"n_steps_budget":900.0,"object_pos_end":[0.521,-0.02293,0.1213],"object_pos_start":[0.5136,-0.02255,0.02569],"object_to_goal_dist_end":0.20424,"object_to_goal_dist_start":0.26555,"object_z_max":0.12041,"peak_contact_force":0.08262,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4589.0,"raw_peak_contact_force":0.66364,"tcp_end":[0.50704,-0.02236,0.12488],"tcp_start":[0.49971,-0.02206,0.02988],"tcp_to_object_dist_end":0.01443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56331,0.14513,0.37334],"object_pos_start":[0.521,-0.02293,0.1213],"object_to_goal_dist_end":0.15177,"object_to_goal_dist_start":0.20424,"object_z_max":0.37313,"peak_contact_force":0.09221,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37031.0,"raw_peak_contact_force":0.12779,"subtask_id":"transport_arc","tcp_end":[0.5501,0.14168,0.38376],"tcp_start":[0.50704,-0.02236,0.12488],"tcp_to_object_dist_end":0.01718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.56126,0.15258,0.22501],"object_pos_start":[0.56331,0.14513,0.37334],"object_to_goal_dist_end":0.00783,"object_to_goal_dist_start":0.15177,"object_z_max":0.37346,"peak_contact_force":0.09525,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8182.0,"raw_peak_contact_force":0.14166,"subtask_id":"release_1","tcp_end":[0.55094,0.14934,0.24112],"tcp_start":[0.5501,0.14168,0.38376],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80233,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20642,"descend_1.grasp_z_offset":0.00502,"lift_1.lift_height":0.20495,"transport_arc.transport_z_offset":0.05169},"optimized_scores":{"best_composite_score":0.65713,"best_fitness_score":0.97713,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.498,0.04349,-0.00163],"force_p95":0.55617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65797,"mean_force":0.29747,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48647,0.0431,0.03155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.48972,0.06241,0.10149],"force_p95":0.09808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33664,"mean_force":0.06529,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49003,0.04317,0.09899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3793.0,"contact_point_centroid":[0.49149,0.02418,0.10071],"force_p95":0.09237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.309,"mean_force":0.05451,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49006,0.04317,0.09933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":907.0,"contact_point_centroid":[0.55268,0.25077,0.18226],"force_p95":0.11208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29862,"mean_force":0.06862,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5569,0.23224,0.17901]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.04494,-0.00216],"force_p95":0.16877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23329,"mean_force":0.13482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48893,0.04333,0.03167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5003.0,"contact_point_centroid":[0.48949,0.02423,0.03174],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19587,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48771,0.04322,0.03038]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.56413,0.21518,0.1784],"force_p95":0.08756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.187,"mean_force":0.05313,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55696,0.23244,0.17825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11101.0,"contact_point_centroid":[0.53039,0.11861,0.18464],"force_p95":0.08802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14966,"mean_force":0.05267,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52551,0.13671,0.18363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9578.0,"contact_point_centroid":[0.52437,0.16011,0.18731],"force_p95":0.10505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14391,"mean_force":0.0604,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52698,0.14128,0.18384]},{"body_a":"world","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.50118,0.04505,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12363,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49903,0.01771,0.2789]},{"body_a":"world","body_b":"grasp_target","contact_count":2616.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49625,0.03931,0.14482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4250.0,"contact_point_centroid":[0.48776,0.06256,0.03299],"force_p95":0.08432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09329,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48771,0.04322,0.03039]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57235,0.24219,0.15358],"final_tcp_position":[0.55821,0.23631,0.16349],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":28.54319,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":28.54319,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":488.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49865,0.03481,0.25285],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2616.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49625,0.04398,0.03949],"tcp_start":[0.49865,0.03481,0.25285],"tcp_to_object_dist_end":0.01438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50119,0.04387,0.02544],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24314,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16507,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11053.0,"raw_peak_contact_force":0.23329,"subtask_id":"grasp_1","tcp_end":[0.48768,0.04322,0.03035],"tcp_start":[0.49625,0.04398,0.03949],"tcp_to_object_dist_end":0.01439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.5112,0.04437,0.17677],"object_pos_start":[0.50119,0.04387,0.02544],"object_to_goal_dist_end":0.2096,"object_to_goal_dist_start":0.24314,"object_z_max":0.17586,"peak_contact_force":0.08714,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6917.0,"raw_peak_contact_force":0.65797,"tcp_end":[0.49666,0.04349,0.18081],"tcp_start":[0.48768,0.04322,0.03035],"tcp_to_object_dist_end":0.01512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.56907,0.23405,0.18088],"object_pos_start":[0.5112,0.04437,0.17677],"object_to_goal_dist_end":0.03608,"object_to_goal_dist_start":0.2096,"object_z_max":0.18087,"peak_contact_force":0.11316,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20679.0,"raw_peak_contact_force":0.14966,"subtask_id":"transport_arc","tcp_end":[0.55619,0.22889,0.18968],"tcp_start":[0.49666,0.04349,0.18081],"tcp_to_object_dist_end":0.01644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":59.0,"n_steps_budget":1000.0,"object_pos_end":[0.57235,0.24219,0.15358],"object_pos_start":[0.56907,0.23405,0.18088],"object_to_goal_dist_end":0.01079,"object_to_goal_dist_start":0.03608,"object_z_max":0.18088,"peak_contact_force":0.11268,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2087.0,"raw_peak_contact_force":0.29862,"subtask_id":"release_1","tcp_end":[0.55821,0.23631,0.16349],"tcp_start":[0.55619,0.22889,0.18968],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84234,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25952,"descend_1.grasp_z_offset":0.00511,"lift_1.lift_height":0.19438,"transport_arc.transport_z_offset":0.2369},"optimized_scores":{"best_composite_score":0.65822,"best_fitness_score":0.97822,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.4734,-0.01953,-0.00154],"force_p95":0.54745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61321,"mean_force":0.25326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46271,-0.01926,0.03299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2876.0,"contact_point_centroid":[0.46492,-0.03863,0.09781],"force_p95":0.08564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30698,"mean_force":0.0632,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46568,-0.0194,0.09519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3467.0,"contact_point_centroid":[0.46649,-0.00036,0.09638],"force_p95":0.08179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30382,"mean_force":0.05452,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46565,-0.0194,0.09483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.61468,0.16437,0.30638],"force_p95":0.09099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21662,"mean_force":0.06165,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61758,0.14569,0.30389]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02015,-0.00207],"force_p95":0.14522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1928,"mean_force":0.12828,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4651,-0.01929,0.03313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5452.0,"contact_point_centroid":[0.62282,0.12745,0.30388],"force_p95":0.09083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1823,"mean_force":0.06102,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61764,0.14576,0.3031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17951.0,"contact_point_centroid":[0.54668,0.04468,0.28626],"force_p95":0.0812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15857,"mean_force":0.05745,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54408,0.06361,0.28404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19402.0,"contact_point_centroid":[0.53862,0.07773,0.27978],"force_p95":0.0781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1513,"mean_force":0.05362,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53976,0.05881,0.27731]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47616,-0.02015,-0.00106],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12212,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49571,-0.00266,0.29842]},{"body_a":"world","body_b":"grasp_target","contact_count":3104.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13411,"mean_force":0.12281,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48012,-0.01325,0.16648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5290.0,"contact_point_centroid":[0.46455,-0.00018,0.03347],"force_p95":0.06466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11739,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4639,-0.01927,0.03195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4436.0,"contact_point_centroid":[0.46333,-0.03856,0.03465],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08525,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46391,-0.01927,0.03195]}],"total_contact_groups":12},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63546,0.15862,0.19111],"final_tcp_position":[0.62578,0.15547,0.20865],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.61321,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":36.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02619],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13462,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":140.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48998,-0.00714,0.295],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02619],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28828,"object_z_max":0.02619,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3104.0,"raw_peak_contact_force":0.13411,"subtask_id":"descend_1","tcp_end":[0.47225,-0.01939,0.0403],"tcp_start":[0.48998,-0.00714,0.295],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01971,0.02574],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28832,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14448,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11526.0,"raw_peak_contact_force":0.1928,"subtask_id":"grasp_1","tcp_end":[0.46387,-0.01927,0.03192],"tcp_start":[0.47225,-0.01939,0.0403],"tcp_to_object_dist_end":0.01367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.48579,-0.02016,0.16483],"object_pos_start":[0.47606,-0.01971,0.02574],"object_to_goal_dist_end":0.2324,"object_to_goal_dist_start":0.28832,"object_z_max":0.16391,"peak_contact_force":0.08204,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6403.0,"raw_peak_contact_force":0.61321,"tcp_end":[0.47169,-0.01958,0.17055],"tcp_start":[0.46387,-0.01927,0.03192],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62439,0.14058,0.37666],"object_pos_start":[0.48579,-0.02016,0.16483],"object_to_goal_dist_end":0.1877,"object_to_goal_dist_start":0.2324,"object_z_max":0.37646,"peak_contact_force":0.07116,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37353.0,"raw_peak_contact_force":0.15857,"subtask_id":"transport_arc","tcp_end":[0.61118,0.13753,0.38833],"tcp_start":[0.47169,-0.01958,0.17055],"tcp_to_object_dist_end":0.01789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.63546,0.15862,0.19111],"object_pos_start":[0.62439,0.14058,0.37666],"object_to_goal_dist_end":0.00423,"object_to_goal_dist_start":0.1877,"object_z_max":0.37672,"peak_contact_force":0.08905,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10779.0,"raw_peak_contact_force":0.21662,"subtask_id":"release_1","tcp_end":[0.62578,0.15547,0.20865],"tcp_start":[0.61118,0.13753,0.38833],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```