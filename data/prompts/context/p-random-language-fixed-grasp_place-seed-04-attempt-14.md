## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1382 | 0.33 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1416 | 0.34 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1756 | 0.20 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1402 | 0.34 | ✅ accepted |
| 10 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0040 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.138) — your mutation base

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

- **Composite score**: 0.138
- **task_score** (E): 0.334
- **fitness_score**: 0.638  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1024 |
| descend_1 | 1.00 | 1.00 | 0.1549 |
| grasp_1 | 1.00 | 1.00 | 0.0134 |
| lift_1 | 1.00 | 1.00 | 0.1187 |
| transport_arc | 1.00 | 1.00 | 0.1944 |
| descend_to_place | 1.00 | 1.00 | 0.0070 |
| release_1 | 1.00 | 1.00 | 0.0210 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.004, 0.202) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 17.103 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.518, 0.004, 0.202)→(0.521, 0.005, 0.048) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.048)→(0.512, 0.005, 0.037) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.000 | 0.143 | 0.194 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.037)→(0.508, 0.005, 0.156) | (0.526, 0.005, 0.026)→(0.525, 0.005, 0.139) | 0.249→0.207 | 1.00 / 23.667 | 0.108 | 0.520 |
| transport_arc | approach | 1.00 / step_budget | (0.508, 0.005, 0.156)→(0.601, 0.160, 0.186) | (0.525, 0.005, 0.139)→(0.565, 0.100, 0.041) | 0.207→0.167 | 1.00 / 15.000 | 91005.507 | 1.417 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.160, 0.186)→(0.602, 0.164, 0.185) | (0.565, 0.100, 0.041)→(0.565, 0.101, 0.039) | 0.167→0.168 | 1.00 / 13.667 | 0.117 | 0.254 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.164, 0.185)→(0.597, 0.163, 0.205) | (0.565, 0.101, 0.039)→(0.564, 0.100, 0.020) | 0.168→0.187 | 1.00 / 3.333 | 0.159 | 0.371 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.584
- phase_score: 0.688
- phase_breakdown.approach_1_score: 0.014
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.890
- phase_breakdown.release_1_score: 0.514
- phase_breakdown.transport_arc_score: 0.674
- grasp_place_fitness: 0.763

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.763
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.584
- **Median Q (composite search score)**: 0.105
- **K-run variance**: 0.0083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87597,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10692,"descend_1.grasp_z_offset":1e-05,"descend_to_place.place_speed":0.18834,"descend_to_place.place_z_offset":0.01933,"lift_1.lift_height":0.12873,"transport_arc.arc_height":0.29684,"transport_arc.transport_speed":0.36795},"optimized_scores":{"best_composite_score":0.10542,"best_fitness_score":0.60542,"best_task_score":0.26456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":951.0,"contact_point_centroid":[0.5883,0.08249,-0.00307],"force_p95":0.64123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85669,"mean_force":0.18159,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.604,0.10513,0.19494]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54155,0.00076,-0.00135],"force_p95":0.5286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56374,"mean_force":0.11997,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52789,0.00082,0.03523]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4999.0,"contact_point_centroid":[0.52873,-0.01806,0.08467],"force_p95":0.11224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32799,"mean_force":0.07652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52531,0.00078,0.08247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1522.0,"contact_point_centroid":[0.54242,-0.00074,0.16025],"force_p95":0.19018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32305,"mean_force":0.10869,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53665,0.01784,0.15962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5269.0,"contact_point_centroid":[0.52881,0.01955,0.083],"force_p95":0.1099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30867,"mean_force":0.07353,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52536,0.00078,0.08106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1937.0,"contact_point_centroid":[0.54412,0.03812,0.1612],"force_p95":0.14134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29076,"mean_force":0.0897,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53813,0.01992,0.16145]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15591,"mean_force":0.12542,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53043,0.00087,0.0354]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51625,0.00044,0.22814]},{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.58809,0.08336,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63594,0.14758,0.18911]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53561,0.00095,0.09993]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58809,0.08336,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63537,0.15064,0.19359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53045,-0.01835,0.03667],"force_p95":0.07623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11922,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00085,0.03401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53036,0.01992,0.0358],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09543,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52921,0.00085,0.03401]},{"body_a":"left_finger","body_b":"right_finger","contact_count":813.0,"contact_point_centroid":[0.61032,0.11261,0.19735],"force_p95":0.01278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0187,"mean_force":0.01083,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60986,0.1126,0.1952]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.63855,0.15148,0.19281],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63797,0.15146,0.19062]},{"body_a":"left_finger","body_b":"right_finger","contact_count":272.0,"contact_point_centroid":[0.63637,0.1476,0.19149],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63595,0.14758,0.18911]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58809,0.08336,0.01602],"final_tcp_position":[0.63921,0.15151,0.19355],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273016.29543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":51.06316,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5348,0.00092,0.15423],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":820.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53819,0.00101,0.04477],"tcp_start":[0.5348,0.00092,0.15423],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00073,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13051,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15591,"subtask_id":"grasp_1","tcp_end":[0.52918,0.00085,0.03397],"tcp_start":[0.53819,0.00101,0.04477],"tcp_to_object_dist_end":0.01705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":364.0,"n_steps_budget":810.0,"object_pos_end":[0.54306,0.00076,0.12908],"object_pos_start":[0.54419,0.00073,0.02587],"object_to_goal_dist_end":0.19883,"object_to_goal_dist_start":0.25052,"object_z_max":0.12883,"peak_contact_force":0.10339,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10344.0,"raw_peak_contact_force":0.56374,"tcp_end":[0.52524,0.00078,0.14324],"tcp_start":[0.52918,0.00085,0.03397],"tcp_to_object_dist_end":0.02276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.58809,0.08336,0.01602],"object_pos_start":[0.54306,0.00076,0.12908],"object_to_goal_dist_end":0.19946,"object_to_goal_dist_start":0.19883,"object_z_max":0.15637,"peak_contact_force":273016.29543,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5223.0,"raw_peak_contact_force":1.85669,"subtask_id":"transport_arc","tcp_end":[0.63414,0.14391,0.1877],"tcp_start":[0.52524,0.00078,0.14324],"tcp_to_object_dist_end":0.18778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.58809,0.08336,0.01602],"object_pos_start":[0.58809,0.08336,0.01602],"object_to_goal_dist_end":0.19946,"object_to_goal_dist_start":0.19946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":528.0,"raw_peak_contact_force":0.12264,"subtask_id":"release_1","tcp_end":[0.63921,0.15151,0.19355],"tcp_start":[0.63414,0.14391,0.1877],"tcp_to_object_dist_end":0.19691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58809,0.08336,0.01602],"object_pos_start":[0.58809,0.08336,0.01602],"object_to_goal_dist_end":0.19946,"object_to_goal_dist_start":0.19946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63389,0.15018,0.21273],"tcp_start":[0.63921,0.15151,0.19355],"tcp_to_object_dist_end":0.21274,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81752,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19889,"descend_1.grasp_z_offset":0.0028,"descend_to_place.place_speed":0.21355,"descend_to_place.place_z_offset":-0.00705,"lift_1.lift_height":0.15707,"transport_arc.arc_height":0.23693,"transport_arc.transport_speed":0.31998},"optimized_scores":{"best_composite_score":0.26271,"best_fitness_score":0.76271,"best_task_score":0.58358},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.58787,0.16665,-0.00604],"force_p95":0.81484,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86907,"mean_force":0.36637,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58387,0.1658,0.11994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.59403,0.18619,0.10851],"force_p95":0.10381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5204,"mean_force":0.07112,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5883,0.16727,0.10841]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.5279,0.02819,-0.00147],"force_p95":0.48755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51758,"mean_force":0.10978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5151,0.02887,0.03909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":773.0,"contact_point_centroid":[0.59442,0.14861,0.1088],"force_p95":0.0975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51749,"mean_force":0.06917,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5883,0.16728,0.10842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":278.0,"contact_point_centroid":[0.59487,0.1855,0.116],"force_p95":0.16902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51539,"mean_force":0.09079,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5903,0.16662,0.11596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":278.0,"contact_point_centroid":[0.59492,0.1479,0.11594],"force_p95":0.1412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50734,"mean_force":0.08843,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5903,0.16659,0.11607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4334.0,"contact_point_centroid":[0.56038,0.08446,0.16362],"force_p95":0.13997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45037,"mean_force":0.09221,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55481,0.10319,0.16216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4967.0,"contact_point_centroid":[0.55905,0.11888,0.16453],"force_p95":0.11774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41219,"mean_force":0.08158,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55318,0.10044,0.16367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6343.0,"contact_point_centroid":[0.51597,0.00988,0.10148],"force_p95":0.11158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31749,"mean_force":0.07462,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51264,0.02871,0.09931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6614.0,"contact_point_centroid":[0.51587,0.04754,0.0981],"force_p95":0.11159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31448,"mean_force":0.07278,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51267,0.02871,0.09618]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03054,-0.00216],"force_p95":0.16804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23842,"mean_force":0.1346,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51764,0.02904,0.03896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.51733,0.00975,0.04039],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15746,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51646,0.02897,0.03763]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.5305,0.03079,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50917,0.01039,0.27266]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52162,0.02577,0.14566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.51727,0.04815,0.03943],"force_p95":0.07489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08074,"mean_force":0.04443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51646,0.02897,0.03764]}],"total_contact_groups":15},"final_pose_error":0.01923,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59341,0.1655,0.02878],"final_tcp_position":[0.59091,0.16772,0.11284],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.86907,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.51979,0.02217,0.24301],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.52521,0.02951,0.04793],"tcp_start":[0.51979,0.02217,0.24301],"tcp_to_object_dist_end":0.02257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02926,0.02546],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15967,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10905.0,"raw_peak_contact_force":0.23842,"subtask_id":"grasp_1","tcp_end":[0.51643,0.02896,0.0376],"tcp_start":[0.52521,0.02951,0.04793],"tcp_to_object_dist_end":0.01855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":452.0,"n_steps_budget":990.0,"object_pos_end":[0.52944,0.02909,0.15639],"object_pos_start":[0.53045,0.02926,0.02546],"object_to_goal_dist_end":0.17285,"object_to_goal_dist_start":0.18487,"object_z_max":0.15613,"peak_contact_force":0.11225,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13038.0,"raw_peak_contact_force":0.51758,"tcp_end":[0.51282,0.02872,0.17521],"tcp_start":[0.51643,0.02896,0.0376],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.595,0.16579,0.09098],"object_pos_start":[0.52944,0.02909,0.15639],"object_to_goal_dist_end":0.02234,"object_to_goal_dist_start":0.17285,"object_z_max":0.15678,"peak_contact_force":0.1036,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9301.0,"raw_peak_contact_force":0.45037,"subtask_id":"transport_arc","tcp_end":[0.59105,0.1659,0.11895],"tcp_start":[0.51282,0.02872,0.17521],"tcp_to_object_dist_end":0.02824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.59644,0.16811,0.08488],"object_pos_start":[0.595,0.16579,0.09098],"object_to_goal_dist_end":0.02597,"object_to_goal_dist_start":0.02234,"object_z_max":0.09098,"peak_contact_force":0.10447,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":556.0,"raw_peak_contact_force":0.51539,"subtask_id":"release_1","tcp_end":[0.59091,0.16772,0.11284],"tcp_start":[0.59105,0.1659,0.11895],"tcp_to_object_dist_end":0.0285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59341,0.1655,0.02878],"object_pos_start":[0.59644,0.16811,0.08488],"object_to_goal_dist_end":0.08079,"object_to_goal_dist_start":0.02597,"object_z_max":0.08488,"peak_contact_force":0.23261,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1737.0,"raw_peak_contact_force":0.86907,"subtask_id":"release_1","tcp_end":[0.5837,0.16575,0.13313],"tcp_start":[0.59091,0.16772,0.11284],"tcp_to_object_dist_end":0.10479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91406,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1612,"descend_1.grasp_z_offset":0.00479,"descend_to_place.place_speed":0.29966,"descend_to_place.place_z_offset":0.0075,"lift_1.lift_height":0.12847,"transport_arc.arc_height":0.18341,"transport_arc.transport_speed":0.28307},"optimized_scores":{"best_composite_score":0.04661,"best_fitness_score":0.54661,"best_task_score":0.15471},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1443.0,"contact_point_centroid":[0.51106,0.05055,-0.0028],"force_p95":0.34693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94369,"mean_force":0.16523,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54002,0.0955,0.26778]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50112,-0.01489,-0.00138],"force_p95":0.46035,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4801,"mean_force":0.11017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48985,-0.01503,0.04217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1701.0,"contact_point_centroid":[0.4944,0.0094,0.18114],"force_p95":0.15483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38396,"mean_force":0.09594,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48829,-0.00898,0.18045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5457.0,"contact_point_centroid":[0.48939,0.00406,0.09158],"force_p95":0.10758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29506,"mean_force":0.06731,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4875,-0.01498,0.08912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1538.0,"contact_point_centroid":[0.49375,-0.02858,0.1777],"force_p95":0.15552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29056,"mean_force":0.0967,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48786,-0.01006,0.17655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5973.0,"contact_point_centroid":[0.48947,-0.03391,0.08987],"force_p95":0.10334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28918,"mean_force":0.06288,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48749,-0.01498,0.08813]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.0156,-0.00206],"force_p95":0.1396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18718,"mean_force":0.12736,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49223,-0.01505,0.04207]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.50382,-0.01567,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49985,-0.00571,0.25668]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49909,-0.01359,0.13048]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51052,0.05086,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57662,0.17197,0.25032]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51052,0.05086,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57407,0.17264,0.25044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5077.0,"contact_point_centroid":[0.49097,0.00421,0.04399],"force_p95":0.06694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10022,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4911,-0.01504,0.04087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.49084,-0.03429,0.0435],"force_p95":0.06541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08473,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4911,-0.01504,0.04088]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1424.0,"contact_point_centroid":[0.54298,0.10075,0.27158],"force_p95":0.01219,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01573,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54263,0.10074,0.26933]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.57621,0.17347,0.24847],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57601,0.17346,0.24626]},{"body_a":"left_finger","body_b":"right_finger","contact_count":87.0,"contact_point_centroid":[0.57667,0.17197,0.25293],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.01028,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57661,0.17196,0.25032]}],"total_contact_groups":16},"final_pose_error":0.01817,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51052,0.05086,0.01602],"final_tcp_position":[0.57723,0.17343,0.2493],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.94369,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":696.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50044,-0.01212,0.21019],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49953,-0.01513,0.05021],"tcp_start":[0.50044,-0.01212,0.21019],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01518,0.02577],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31211,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1376,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12274.0,"raw_peak_contact_force":0.18718,"subtask_id":"grasp_1","tcp_end":[0.49107,-0.01504,0.04084],"tcp_start":[0.49953,-0.01513,0.05021],"tcp_to_object_dist_end":0.01968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":345.0,"n_steps_budget":810.0,"object_pos_end":[0.50339,-0.015,0.13096],"object_pos_start":[0.50373,-0.01518,0.02577],"object_to_goal_dist_end":0.24837,"object_to_goal_dist_start":0.31211,"object_z_max":0.13069,"peak_contact_force":0.10714,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11504.0,"raw_peak_contact_force":0.4801,"tcp_end":[0.48739,-0.01497,0.14993],"tcp_start":[0.49107,-0.01504,0.04084],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.51052,0.05086,0.01602],"object_pos_start":[0.50339,-0.015,0.13096],"object_to_goal_dist_end":0.27993,"object_to_goal_dist_start":0.24837,"object_z_max":0.18466,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6106.0,"raw_peak_contact_force":1.94369,"subtask_id":"transport_arc","tcp_end":[0.57708,0.17088,0.25216],"tcp_start":[0.48739,-0.01497,0.14993],"tcp_to_object_dist_end":0.27313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.51052,0.05086,0.01602],"object_pos_start":[0.51052,0.05086,0.01602],"object_to_goal_dist_end":0.27993,"object_to_goal_dist_start":0.27993,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":167.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57723,0.17343,0.2493],"tcp_start":[0.57708,0.17088,0.25216],"tcp_to_object_dist_end":0.27183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51052,0.05086,0.01602],"object_pos_start":[0.51052,0.05086,0.01602],"object_to_goal_dist_end":0.27993,"object_to_goal_dist_start":0.27993,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57299,0.17219,0.27031],"tcp_start":[0.57723,0.17343,0.2493],"tcp_to_object_dist_end":0.28859,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```