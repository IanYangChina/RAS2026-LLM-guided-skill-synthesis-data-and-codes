## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0375 | 0.36 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0674 | 0.39 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0002 | 0.20 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1049 | 0.20 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3009 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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

## Current Skill (Q=-0.038) — your mutation base

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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
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
  subtask_id: grasp_1
- id: lift_1
  type: lift
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.038
- **task_score** (E): 0.356
- **fitness_score**: 0.562  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1439 |
| descend_1 | 1.00 | 1.00 | 0.1141 |
| grasp_1 | 1.00 | 1.00 | 0.0110 |
| lift_1 | 0.33 | 1.00 | 0.1188 |
| transport_1 | 1.00 | 1.00 | 0.2181 |
| place_descend | 1.00 | 1.00 | 0.0242 |
| release_1 | 1.00 | 1.00 | 0.0204 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.162) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.490, -0.014, 0.162)→(0.488, -0.015, 0.048) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.048)→(0.481, -0.015, 0.040) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.025) | 0.281→0.281 | 1.00 / 38.333 | 0.180 | 0.210 |
| lift_1 | lift | 0.33 / step_budget | (0.481, -0.015, 0.040)→(0.485, -0.015, 0.159) | (0.493, -0.015, 0.025)→(0.491, -0.015, 0.087) | 0.281→0.264 | 1.00 / 29.333 | 3249.795 | 0.514 |
| transport_1 | approach | 1.00 / step_budget | (0.485, -0.015, 0.159)→(0.616, 0.154, 0.156) | (0.491, -0.015, 0.087)→(0.585, 0.106, 0.089) | 0.264→0.116 | 1.00 / 30.333 | 0.096 | 0.165 |
| place_descend | approach | 1.00 / step_budget | (0.616, 0.154, 0.156)→(0.631, 0.173, 0.155) | (0.585, 0.106, 0.089)→(0.598, 0.121, 0.087) | 0.116→0.107 | 1.00 / 25.333 | 0.096 | 0.205 |
| release_1 | release | 1.00 / step_budget | (0.631, 0.173, 0.155)→(0.625, 0.171, 0.175) | (0.598, 0.121, 0.087)→(0.589, 0.120, 0.026) | 0.107→0.168 | 1.00 / 3.333 | 0.128 | 0.773 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.546
- phase_score: 0.585
- phase_breakdown.transport_arc_score: 0.449
- phase_breakdown.approach_1_score: 0.075
- phase_breakdown.descend_1_score: 0.785
- phase_breakdown.release_1_score: 0.707
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.752

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.752
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: 0.046
- **K-run variance**: 0.0394
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.393


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.824,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09385,"approach_1.speed":0.07379,"descend_1.grasp_z_offset":-0.00997,"descend_1.speed":0.01576,"lift_1.lift_height":0.24104,"lift_1.speed":0.05326,"place_descend.speed":0.09874,"release_1.duration":0.57823,"transport_1.speed":0.29338},"optimized_scores":{"best_composite_score":0.04636,"best_fitness_score":0.64636,"best_task_score":0.3337},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.61661,0.15518,-0.00868],"force_p95":1.29646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37566,"mean_force":0.47304,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6208,0.15538,0.19076]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.47272,-0.0195,-0.00115],"force_p95":0.42289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59024,"mean_force":0.08887,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46269,-0.0197,0.03206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20475.0,"contact_point_centroid":[0.4626,-0.00047,0.08162],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28818,"mean_force":0.0495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46278,-0.01963,0.07975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20578.0,"contact_point_centroid":[0.46259,-0.03878,0.08087],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28445,"mean_force":0.04949,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46276,-0.01963,0.07919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17298.0,"contact_point_centroid":[0.53532,0.04019,0.15004],"force_p95":0.08681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20494,"mean_force":0.05841,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53551,0.05942,0.14845]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16658.0,"contact_point_centroid":[0.61909,0.12821,0.17558],"force_p95":0.08101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19683,"mean_force":0.05671,"phase_index":5.0,"phase_name":"place_descend","phase_type":"approach","tcp_position_centroid":[0.61618,0.14734,0.174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20292.0,"contact_point_centroid":[0.61725,0.16602,0.17461],"force_p95":0.07498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17592,"mean_force":0.04779,"phase_index":5.0,"phase_name":"place_descend","phase_type":"approach","tcp_position_centroid":[0.61586,0.14704,0.1738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21234.0,"contact_point_centroid":[0.53617,0.0789,0.15022],"force_p95":0.07345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17386,"mean_force":0.0472,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53597,0.05994,0.1486]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02005,-0.00203],"force_p95":0.1339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17121,"mean_force":0.12575,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4652,-0.01976,0.03159]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48643,-0.009,0.21654]},{"body_a":"world","body_b":"grasp_target","contact_count":2748.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47134,-0.01913,0.08309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1006.0,"contact_point_centroid":[0.62729,0.17555,0.17615],"force_p95":0.08396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09619,"mean_force":0.0506,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62476,0.15658,0.17672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5077.0,"contact_point_centroid":[0.46364,-0.00049,0.03362],"force_p95":0.06615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09209,"mean_force":0.04288,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.01973,0.0305]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.62759,0.13757,0.17664],"force_p95":0.08504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09188,"mean_force":0.05315,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62476,0.15658,0.17673]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5385.0,"contact_point_centroid":[0.46354,-0.03898,0.03302],"force_p95":0.06457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08362,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.01973,0.0305]}],"total_contact_groups":15},"final_pose_error":0.01115,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61523,0.15464,0.02625],"final_tcp_position":[0.62637,0.15699,0.18032],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.37566,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47452,-0.0184,0.13327],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2748.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47157,-0.01992,0.03796],"tcp_start":[0.47452,-0.0184,0.13327],"tcp_to_object_dist_end":0.0128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01976,0.02586],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1323,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12262.0,"raw_peak_contact_force":0.17121,"subtask_id":"grasp_1","tcp_end":[0.46407,-0.01973,0.03047],"tcp_start":[0.47157,-0.01992,0.03796],"tcp_to_object_dist_end":0.01283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47335,-0.01953,0.11339],"object_pos_start":[0.47604,-0.01976,0.02586],"object_to_goal_dist_end":0.2506,"object_to_goal_dist_start":0.2883,"object_z_max":0.11328,"peak_contact_force":0.07866,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41218.0,"raw_peak_contact_force":0.59024,"tcp_end":[0.46515,-0.01962,0.12583],"tcp_start":[0.46407,-0.01973,0.03047],"tcp_to_object_dist_end":0.01491,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61176,0.13843,0.15196],"object_pos_start":[0.47335,-0.01953,0.11339],"object_to_goal_dist_end":0.0476,"object_to_goal_dist_start":0.2506,"object_z_max":0.1519,"peak_contact_force":0.08003,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38532.0,"raw_peak_contact_force":0.20494,"subtask_id":"transport_arc","tcp_end":[0.60905,0.13801,0.17462],"tcp_start":[0.46515,-0.01962,0.12583],"tcp_to_object_dist_end":0.02282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62881,0.15713,0.1534],"object_pos_start":[0.61176,0.13843,0.15196],"object_to_goal_dist_end":0.03676,"object_to_goal_dist_start":0.0476,"object_z_max":0.1534,"peak_contact_force":0.08524,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36950.0,"raw_peak_contact_force":0.19683,"tcp_end":[0.62637,0.15699,0.18032],"tcp_start":[0.60905,0.13801,0.17462],"tcp_to_object_dist_end":0.02703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61523,0.15464,0.02625],"object_pos_start":[0.62881,0.15713,0.1534],"object_to_goal_dist_end":0.16463,"object_to_goal_dist_start":0.03676,"object_z_max":0.1534,"peak_contact_force":0.1307,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2100.0,"raw_peak_contact_force":1.37566,"subtask_id":"release_1","tcp_end":[0.62075,0.15537,0.2],"tcp_start":[0.62637,0.15699,0.18032],"tcp_to_object_dist_end":0.17384,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94656,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12006,"approach_1.speed":0.01404,"descend_1.grasp_z_offset":-0.00984,"descend_1.speed":0.04387,"lift_1.lift_height":0.22081,"lift_1.speed":0.05065,"place_descend.speed":0.04291,"release_1.duration":0.99557,"transport_1.speed":0.4911},"optimized_scores":{"best_composite_score":0.15247,"best_fitness_score":0.75247,"best_task_score":0.54607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":370.0,"contact_point_centroid":[0.60893,0.2028,-0.00335],"force_p95":0.52324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82043,"mean_force":0.18641,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61725,0.20259,0.11081]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.45565,-0.02551,-0.00115],"force_p95":0.42519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58127,"mean_force":0.08929,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44572,-0.02568,0.03333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20898.0,"contact_point_centroid":[0.61249,0.21093,0.1044],"force_p95":0.07013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29547,"mean_force":0.04684,"phase_index":5.0,"phase_name":"place_descend","phase_type":"approach","tcp_position_centroid":[0.61251,0.19181,0.10276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20494.0,"contact_point_centroid":[0.44583,-0.04476,0.08411],"force_p95":0.07146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26922,"mean_force":0.0497,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44605,-0.02559,0.08244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20729.0,"contact_point_centroid":[0.44589,-0.00644,0.08525],"force_p95":0.07038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26118,"mean_force":0.04885,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44609,-0.02559,0.0833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19048.0,"contact_point_centroid":[0.61162,0.17229,0.10468],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20933,"mean_force":0.05045,"phase_index":5.0,"phase_name":"place_descend","phase_type":"approach","tcp_position_centroid":[0.61221,0.19147,0.10271]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02622,-0.00205],"force_p95":0.1382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18843,"mean_force":0.12681,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44809,-0.02577,0.03273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21318.0,"contact_point_centroid":[0.5253,0.09628,0.12134],"force_p95":0.0744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16727,"mean_force":0.04721,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52525,0.0772,0.11912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19358.0,"contact_point_centroid":[0.52805,0.06188,0.12076],"force_p95":0.08046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16499,"mean_force":0.05127,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5283,0.08112,0.11871]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47906,-0.01145,0.23019]},{"body_a":"world","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45506,-0.02478,0.09663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44634,-0.00648,0.03342],"force_p95":0.06501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09809,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44703,-0.02573,0.03172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.62131,0.18518,0.10216],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08754,"mean_force":0.04798,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62213,0.20438,0.10106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5399.0,"contact_point_centroid":[0.44634,-0.04501,0.03321],"force_p95":0.06519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08637,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44703,-0.02573,0.03172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.62221,0.22344,0.10167],"force_p95":0.06988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08095,"mean_force":0.04174,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62212,0.20438,0.10106]}],"total_contact_groups":15},"final_pose_error":0.01167,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60818,0.20279,0.02623],"final_tcp_position":[0.62405,0.205,0.10469],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.82043,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45899,-0.02366,0.15959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3060.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45426,-0.026,0.03867],"tcp_start":[0.45899,-0.02366,0.15959],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02582,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30339,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13636,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12508.0,"raw_peak_contact_force":0.18843,"subtask_id":"grasp_1","tcp_end":[0.447,-0.02573,0.0317],"tcp_start":[0.45426,-0.026,0.03867],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45659,-0.02553,0.12049],"object_pos_start":[0.45845,-0.02582,0.02581],"object_to_goal_dist_end":0.29119,"object_to_goal_dist_start":0.30339,"object_z_max":0.12042,"peak_contact_force":0.0698,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41379.0,"raw_peak_contact_force":0.58127,"tcp_end":[0.44886,-0.0256,0.13366],"tcp_start":[0.447,-0.02573,0.0317],"tcp_to_object_dist_end":0.01527,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59853,0.1783,0.08934],"object_pos_start":[0.45659,-0.02553,0.12049],"object_to_goal_dist_end":0.05007,"object_to_goal_dist_start":0.29119,"object_z_max":0.12051,"peak_contact_force":0.08427,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40676.0,"raw_peak_contact_force":0.16727,"subtask_id":"transport_arc","tcp_end":[0.60403,0.17851,0.10802],"tcp_start":[0.44886,-0.0256,0.13366],"tcp_to_object_dist_end":0.01947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6216,0.20479,0.08168],"object_pos_start":[0.59853,0.1783,0.08934],"object_to_goal_dist_end":0.03372,"object_to_goal_dist_start":0.05007,"object_z_max":0.08934,"peak_contact_force":0.07896,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39946.0,"raw_peak_contact_force":0.29547,"tcp_end":[0.62405,0.205,0.10469],"tcp_start":[0.60403,0.17851,0.10802],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60818,0.20279,0.02623],"object_pos_start":[0.6216,0.20479,0.08168],"object_to_goal_dist_end":0.09075,"object_to_goal_dist_start":0.03372,"object_z_max":0.08168,"peak_contact_force":0.12958,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2656.0,"raw_peak_contact_force":0.82043,"subtask_id":"release_1","tcp_end":[0.61708,0.20253,0.12407],"tcp_start":[0.62405,0.205,0.10469],"tcp_to_object_dist_end":0.09824,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21466,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15909,"approach_1.speed":0.05154,"descend_1.grasp_z_offset":0.00801,"descend_1.speed":0.03501,"lift_1.lift_height":0.20767,"lift_1.speed":0.11193,"place_descend.speed":0.06208,"release_1.duration":0.64995,"transport_1.speed":0.27443},"optimized_scores":{"best_composite_score":-0.31142,"best_fitness_score":0.28858,"best_task_score":0.18884},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3449.0,"contact_point_centroid":[0.54403,0.00078,-0.00207],"force_p95":0.18733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3705,"mean_force":0.12715,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53342,0.00019,0.13803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":61.0,"contact_point_centroid":[0.53736,-0.01239,0.05293],"force_p95":0.21,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29901,"mean_force":0.16887,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5296,0.00087,0.05963]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54436,0.0014,-0.00222],"force_p95":0.22358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27111,"mean_force":0.14113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53167,0.00092,0.06056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.52974,0.01288,0.05598],"force_p95":0.09297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19753,"mean_force":0.03269,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52885,0.00084,0.0612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2542.0,"contact_point_centroid":[0.53111,-0.0176,0.05375],"force_p95":0.11639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1698,"mean_force":0.08074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53049,0.00089,0.05912]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51666,0.00047,0.24659]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53629,0.001,0.11455]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54405,0.00146,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58937,0.07625,0.19767]},{"body_a":"world","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.54405,0.00146,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"approach","tcp_position_centroid":[0.63884,0.15147,0.17943]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54405,0.00146,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6389,0.15495,0.18123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2932.0,"contact_point_centroid":[0.53106,0.01869,0.05419],"force_p95":0.08776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09102,"mean_force":0.06193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53049,0.00089,0.05912]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3097.0,"contact_point_centroid":[0.53445,9e-05,0.15268],"force_p95":0.01126,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01596,"mean_force":0.01065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53435,9e-05,0.15039]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4245.0,"contact_point_centroid":[0.58956,0.07621,0.19996],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58934,0.07621,0.19769]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3574.0,"contact_point_centroid":[0.63919,0.15148,0.18171],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01054,"phase_index":5.0,"phase_name":"place_descend","phase_type":"approach","tcp_position_centroid":[0.63883,0.15146,0.17943]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.64209,0.15577,0.18044],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.0102,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64162,0.15575,0.17822]}],"total_contact_groups":15},"final_pose_error":0.011,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54405,0.00146,0.02602],"final_tcp_position":[0.64295,0.15609,0.18135],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9749.2379,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53613,0.00097,0.19463],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53833,0.00103,0.06877],"tcp_start":[0.53613,0.00097,0.19463],"tcp_to_object_dist_end":0.04317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5444,-0.00043,0.02384],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2525,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.27217,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7274.0,"raw_peak_contact_force":0.27111,"subtask_id":"grasp_1","tcp_end":[0.53047,0.0009,0.05909],"tcp_start":[0.53833,0.00103,0.06877],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":895.0,"n_steps_budget":960.0,"object_pos_end":[0.54405,0.00146,0.02602],"object_pos_start":[0.5444,-0.00043,0.02384],"object_to_goal_dist_end":0.25002,"object_to_goal_dist_start":0.2525,"object_z_max":0.02786,"peak_contact_force":9749.2379,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7243.0,"raw_peak_contact_force":0.3705,"tcp_end":[0.54046,-0.00042,0.2177],"tcp_start":[0.53047,0.0009,0.05909],"tcp_to_object_dist_end":0.19172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54405,0.00146,0.02602],"object_pos_start":[0.54405,0.00146,0.02602],"object_to_goal_dist_end":0.25002,"object_to_goal_dist_start":0.25002,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8245.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.63628,0.1456,0.18432],"tcp_start":[0.54046,-0.00042,0.2177],"tcp_to_object_dist_end":0.23312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.54405,0.00146,0.02602],"object_pos_start":[0.54405,0.00146,0.02602],"object_to_goal_dist_end":0.25002,"object_to_goal_dist_start":0.25002,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6958.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64295,0.15609,0.18135],"tcp_start":[0.63628,0.1456,0.18432],"tcp_to_object_dist_end":0.24046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54405,0.00146,0.02602],"object_pos_start":[0.54405,0.00146,0.02602],"object_to_goal_dist_end":0.25002,"object_to_goal_dist_start":0.25002,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63734,0.15447,0.20037],"tcp_start":[0.64295,0.15609,0.18135],"tcp_to_object_dist_end":0.25003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```