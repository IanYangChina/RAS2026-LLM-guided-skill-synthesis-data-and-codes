## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1402 | 0.34 | ❌ rejected |
| 10 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0040 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.0589 | 0.27 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1032 | 0.20 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1431 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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

## Current Skill (Q=0.140) — your mutation base

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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.140
- **task_score** (E): 0.337
- **fitness_score**: 0.640  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0658 |
| descend_1 | 1.00 | 1.00 | 0.1927 |
| grasp_1 | 1.00 | 1.00 | 0.0134 |
| lift_1 | 1.00 | 1.00 | 0.1317 |
| transport_arc | 1.00 | 1.00 | 0.1883 |
| descend_to_place | 1.00 | 1.00 | 0.0046 |
| release_1 | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.004, 0.240) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 13.996 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, 0.004, 0.240)→(0.521, 0.005, 0.048) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.048)→(0.512, 0.005, 0.037) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.000 | 0.143 | 0.196 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.037)→(0.509, 0.005, 0.169) | (0.526, 0.005, 0.026)→(0.525, 0.005, 0.151) | 0.249→0.201 | 1.00 / 22.333 | 0.113 | 0.522 |
| transport_arc | approach | 1.00 / step_budget | (0.509, 0.005, 0.169)→(0.601, 0.160, 0.186) | (0.525, 0.005, 0.151)→(0.567, 0.107, 0.041) | 0.201→0.164 | 1.00 / 16.333 | 0.115 | 1.546 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.160, 0.186)→(0.601, 0.162, 0.182) | (0.567, 0.107, 0.041)→(0.567, 0.108, 0.039) | 0.164→0.164 | 1.00 / 16.333 | 90993.192 | 0.244 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.162, 0.182)→(0.595, 0.161, 0.202) | (0.567, 0.108, 0.039)→(0.566, 0.108, 0.020) | 0.164→0.183 | 1.00 / 3.333 | 0.172 | 0.436 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.582
- phase_score: 0.683
- phase_breakdown.release_1_score: 0.511
- phase_breakdown.approach_1_score: 0.011
- phase_breakdown.descend_1_score: 0.860
- phase_breakdown.transport_arc_score: 0.673
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.765

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.765
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.582
- **Median Q (composite search score)**: 0.096
- **K-run variance**: 0.0080
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.296


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78788,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17334,"descend_1.grasp_z_offset":0.0073,"descend_to_place.place_speed":0.12773,"descend_to_place.place_z_offset":0.00995,"lift_1.lift_height":0.14428,"transport_arc.arc_height":0.24476,"transport_arc.transport_speed":0.34481},"optimized_scores":{"best_composite_score":0.0959,"best_fitness_score":0.5959,"best_task_score":0.25792},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.58254,0.07694,-0.00308],"force_p95":0.64908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88146,"mean_force":0.18264,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60241,0.10255,0.20709]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54166,0.0008,-0.00137],"force_p95":0.44099,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4683,"mean_force":0.10017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52822,0.00083,0.0425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5671.0,"contact_point_centroid":[0.52917,-0.01804,0.09884],"force_p95":0.11415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31654,"mean_force":0.07698,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52567,0.00079,0.09671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1482.0,"contact_point_centroid":[0.54221,0.03446,0.17981],"force_p95":0.14783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29482,"mean_force":0.09081,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53601,0.01615,0.18021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5935.0,"contact_point_centroid":[0.52919,0.01956,0.09677],"force_p95":0.11187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29448,"mean_force":0.07429,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52571,0.00079,0.09483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1305.0,"contact_point_centroid":[0.54088,-0.00419,0.17888],"force_p95":0.18465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26728,"mean_force":0.10056,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5347,0.01429,0.17865]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15389,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53073,0.00088,0.04268]},{"body_a":"world","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.54431,0.00113,-0.00182],"force_p95":0.13761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12332,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51497,0.00041,0.26042]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53066,-0.01835,0.04396],"force_p95":0.07631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12341,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52953,0.00086,0.04128]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.58232,0.07809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63437,0.14503,0.19006]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53436,0.00092,0.13586]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58232,0.07809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63189,0.14625,0.18961]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53058,0.01993,0.04308],"force_p95":0.06838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09426,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52953,0.00086,0.04128]},{"body_a":"left_finger","body_b":"right_finger","contact_count":870.0,"contact_point_centroid":[0.60777,0.10885,0.20889],"force_p95":0.0125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01084,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60733,0.10884,0.2067]},{"body_a":"left_finger","body_b":"right_finger","contact_count":113.0,"contact_point_centroid":[0.6351,0.14502,0.19263],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63436,0.145,0.19008]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.63486,0.14711,0.18885],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6345,0.1471,0.18646]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58232,0.07809,0.01602],"final_tcp_position":[0.63588,0.147,0.18962],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.88146,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":708.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53209,0.00085,0.21874],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5384,0.00102,0.05206],"tcp_start":[0.53209,0.00085,0.21874],"tcp_to_object_dist_end":0.0267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00076,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13078,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15389,"subtask_id":"grasp_1","tcp_end":[0.5295,0.00085,0.04124],"tcp_start":[0.5384,0.00102,0.05206],"tcp_to_object_dist_end":0.02128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":415.0,"n_steps_budget":900.0,"object_pos_end":[0.54155,0.00087,0.14451],"object_pos_start":[0.54421,0.00076,0.02586],"object_to_goal_dist_end":0.19529,"object_to_goal_dist_start":0.2505,"object_z_max":0.14425,"peak_contact_force":0.11231,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11682.0,"raw_peak_contact_force":0.4683,"tcp_end":[0.52576,0.00079,0.16599],"tcp_start":[0.5295,0.00085,0.04124],"tcp_to_object_dist_end":0.02666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.58232,0.07809,0.01602],"object_pos_start":[0.54155,0.00087,0.14451],"object_to_goal_dist_end":0.20327,"object_to_goal_dist_start":0.19529,"object_z_max":0.16712,"peak_contact_force":0.12264,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4633.0,"raw_peak_contact_force":1.88146,"subtask_id":"transport_arc","tcp_end":[0.63424,0.14359,0.19186],"tcp_start":[0.52576,0.00079,0.16599],"tcp_to_object_dist_end":0.19469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.58232,0.07809,0.01602],"object_pos_start":[0.58232,0.07809,0.01602],"object_to_goal_dist_end":0.20327,"object_to_goal_dist_start":0.20327,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":217.0,"raw_peak_contact_force":0.12264,"subtask_id":"release_1","tcp_end":[0.63588,0.147,0.18962],"tcp_start":[0.63424,0.14359,0.19186],"tcp_to_object_dist_end":0.1943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58232,0.07809,0.01602],"object_pos_start":[0.58232,0.07809,0.01602],"object_to_goal_dist_end":0.20327,"object_to_goal_dist_start":0.20327,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63039,0.14578,0.20884],"tcp_start":[0.63588,0.147,0.18962],"tcp_to_object_dist_end":0.20993,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79137,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21238,"descend_1.grasp_z_offset":8e-05,"descend_to_place.place_speed":0.2029,"descend_to_place.place_z_offset":-0.00101,"lift_1.lift_height":0.1531,"transport_arc.arc_height":0.27009,"transport_arc.transport_speed":0.36215},"optimized_scores":{"best_composite_score":0.26473,"best_fitness_score":0.76473,"best_task_score":0.58248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.58653,0.1735,-0.00621],"force_p95":0.88851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06135,"mean_force":0.37481,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58357,0.16492,0.11988]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52759,0.02832,-0.00149],"force_p95":0.52863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56,"mean_force":0.12107,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51499,0.02882,0.03603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":305.0,"contact_point_centroid":[0.59437,0.14671,0.11522],"force_p95":0.145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48705,"mean_force":0.08308,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5899,0.1656,0.1146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4371.0,"contact_point_centroid":[0.55744,0.07955,0.1576],"force_p95":0.13289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47948,"mean_force":0.09089,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55183,0.09822,0.1561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4783.0,"contact_point_centroid":[0.55945,0.12,0.15673],"force_p95":0.11753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39124,"mean_force":0.08284,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55372,0.10153,0.15563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.59461,0.18434,0.11625],"force_p95":0.16203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37948,"mean_force":0.07896,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58991,0.16557,0.11469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":957.0,"contact_point_centroid":[0.59334,0.14759,0.10943],"force_p95":0.09618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3468,"mean_force":0.05795,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5882,0.16646,0.10837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.59339,0.18547,0.1097],"force_p95":0.11093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32794,"mean_force":0.05994,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58807,0.16641,0.10816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6091.0,"contact_point_centroid":[0.51581,0.00981,0.09647],"force_p95":0.11194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3221,"mean_force":0.07514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51251,0.02866,0.09423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6475.0,"contact_point_centroid":[0.51574,0.04747,0.09341],"force_p95":0.11057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32002,"mean_force":0.07216,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51254,0.02866,0.09153]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03049,-0.00217],"force_p95":0.17058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24376,"mean_force":0.13518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51753,0.029,0.03593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3878.0,"contact_point_centroid":[0.51759,0.00972,0.03747],"force_p95":0.08534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15414,"mean_force":0.0542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51634,0.02892,0.0346]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.5305,0.03079,-0.00173],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12369,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50863,0.0098,0.27861]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52115,0.02521,0.15009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4995.0,"contact_point_centroid":[0.51726,0.04808,0.03641],"force_p95":0.07563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0807,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51635,0.02892,0.03461]}],"total_contact_groups":15},"final_pose_error":0.01702,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59358,0.16819,0.02808],"final_tcp_position":[0.59043,0.16675,0.11224],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.06135,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12249,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.51885,0.02109,0.25507],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.52513,0.02947,0.04486],"tcp_start":[0.51885,0.02109,0.25507],"tcp_to_object_dist_end":0.01964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.02916,0.02545],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18496,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16058,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10673.0,"raw_peak_contact_force":0.24376,"subtask_id":"grasp_1","tcp_end":[0.51631,0.02892,0.03456],"tcp_start":[0.52513,0.02947,0.04486],"tcp_to_object_dist_end":0.01682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":438.0,"n_steps_budget":960.0,"object_pos_end":[0.53013,0.02896,0.15219],"object_pos_start":[0.53044,0.02916,0.02545],"object_to_goal_dist_end":0.17155,"object_to_goal_dist_start":0.18496,"object_z_max":0.15193,"peak_contact_force":0.11303,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12646.0,"raw_peak_contact_force":0.56,"tcp_end":[0.51265,0.02867,0.16815],"tcp_start":[0.51631,0.02892,0.03456],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.59511,0.16446,0.09114],"object_pos_start":[0.53013,0.02896,0.15219],"object_to_goal_dist_end":0.02298,"object_to_goal_dist_start":0.17155,"object_z_max":0.15251,"peak_contact_force":0.1004,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9154.0,"raw_peak_contact_force":0.47948,"subtask_id":"transport_arc","tcp_end":[0.59066,0.16478,0.11723],"tcp_start":[0.51265,0.02867,0.16815],"tcp_to_object_dist_end":0.02647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.596,0.16685,0.08618],"object_pos_start":[0.59511,0.16446,0.09114],"object_to_goal_dist_end":0.02546,"object_to_goal_dist_start":0.02298,"object_z_max":0.09114,"peak_contact_force":0.0913,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":637.0,"raw_peak_contact_force":0.48705,"subtask_id":"release_1","tcp_end":[0.59043,0.16675,0.11224],"tcp_start":[0.59066,0.16478,0.11723],"tcp_to_object_dist_end":0.02665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59358,0.16819,0.02808],"object_pos_start":[0.596,0.16685,0.08618],"object_to_goal_dist_end":0.08107,"object_to_goal_dist_start":0.02546,"object_z_max":0.08618,"peak_contact_force":0.27125,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2184.0,"raw_peak_contact_force":1.06135,"subtask_id":"release_1","tcp_end":[0.58341,0.16487,0.13283],"tcp_start":[0.59043,0.16675,0.11224],"tcp_to_object_dist_end":0.10529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77698,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19807,"descend_1.grasp_z_offset":0.00037,"descend_to_place.place_speed":0.18205,"descend_to_place.place_z_offset":-0.00177,"lift_1.lift_height":0.15589,"transport_arc.arc_height":0.27235,"transport_arc.transport_speed":0.34975},"optimized_scores":{"best_composite_score":0.05984,"best_fitness_score":0.55984,"best_task_score":0.17175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1143.0,"contact_point_centroid":[0.52319,0.0786,-0.00301],"force_p95":0.50021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2782,"mean_force":0.16752,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54848,0.11299,0.25581]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50107,-0.01481,-0.0014],"force_p95":0.51334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5372,"mean_force":0.12115,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48984,-0.01495,0.03765]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1697.0,"contact_point_centroid":[0.49986,-0.01679,0.19703],"force_p95":0.17973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33471,"mean_force":0.10215,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49386,0.00174,0.19673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1935.0,"contact_point_centroid":[0.50075,0.02163,0.19832],"force_p95":0.17321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30865,"mean_force":0.09823,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49459,0.00333,0.19857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6425.0,"contact_point_centroid":[0.48986,0.00407,0.0983],"force_p95":0.10985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30259,"mean_force":0.07035,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48744,-0.0149,0.09593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7012.0,"contact_point_centroid":[0.48989,-0.03378,0.09645],"force_p95":0.10552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29556,"mean_force":0.06562,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48744,-0.01491,0.09471]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01556,-0.00206],"force_p95":0.14096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19103,"mean_force":0.12772,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49222,-0.01498,0.03756]},{"body_a":"world","body_b":"grasp_target","contact_count":432.0,"contact_point_centroid":[0.50382,-0.01567,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12378,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5,-0.00481,0.2751]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49911,-0.01275,0.14618]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52293,0.07849,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57638,0.1715,0.24578]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52293,0.07849,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5738,0.17223,0.24541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.49096,0.00429,0.0395],"force_p95":0.06723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09913,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01496,0.03636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5413.0,"contact_point_centroid":[0.49083,-0.03422,0.039],"force_p95":0.0656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07518,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01496,0.03636]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1066.0,"contact_point_centroid":[0.55247,0.12048,0.25884],"force_p95":0.01216,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5522,0.12048,0.25666]},{"body_a":"left_finger","body_b":"right_finger","contact_count":84.0,"contact_point_centroid":[0.57652,0.17154,0.24826],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57639,0.17153,0.24575]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.5762,0.17308,0.24373],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5758,0.17307,0.24124]}],"total_contact_groups":16},"final_pose_error":0.01755,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52293,0.07849,0.01602],"final_tcp_position":[0.57709,0.17304,0.2444],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":272979.36356,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":41.74178,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":432.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50035,-0.01053,0.24658],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49957,-0.01504,0.04568],"tcp_start":[0.50035,-0.01053,0.24658],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01508,0.02576],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13861,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.19103,"subtask_id":"grasp_1","tcp_end":[0.49105,-0.01496,0.03633],"tcp_start":[0.49957,-0.01504,0.04568],"tcp_to_object_dist_end":0.01649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":431.0,"n_steps_budget":990.0,"object_pos_end":[0.50472,-0.01484,0.15658],"object_pos_start":[0.50372,-0.01508,0.02576],"object_to_goal_dist_end":0.23676,"object_to_goal_dist_start":0.31206,"object_z_max":0.15632,"peak_contact_force":0.11441,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13511.0,"raw_peak_contact_force":0.5372,"tcp_end":[0.48755,-0.01489,0.17281],"tcp_start":[0.49105,-0.01496,0.03633],"tcp_to_object_dist_end":0.02363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.52293,0.07849,0.01602],"object_pos_start":[0.50472,-0.01484,0.15658],"object_to_goal_dist_end":0.26426,"object_to_goal_dist_start":0.23676,"object_z_max":0.20041,"peak_contact_force":0.12262,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5841.0,"raw_peak_contact_force":2.2782,"subtask_id":"transport_arc","tcp_end":[0.57672,0.17035,0.24742],"tcp_start":[0.48755,-0.01489,0.17281],"tcp_to_object_dist_end":0.25471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.52293,0.07849,0.01602],"object_pos_start":[0.52293,0.07849,0.01602],"object_to_goal_dist_end":0.26426,"object_to_goal_dist_start":0.26426,"object_z_max":0.01602,"peak_contact_force":272979.36356,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":164.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57709,0.17304,0.2444],"tcp_start":[0.57672,0.17035,0.24742],"tcp_to_object_dist_end":0.25304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52293,0.07849,0.01602],"object_pos_start":[0.52293,0.07849,0.01602],"object_to_goal_dist_end":0.26426,"object_to_goal_dist_start":0.26426,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57269,0.17177,0.2653],"tcp_start":[0.57709,0.17304,0.2444],"tcp_to_object_dist_end":0.27077,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```