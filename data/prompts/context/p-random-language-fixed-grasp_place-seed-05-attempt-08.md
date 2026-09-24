## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2235 | 0.42 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3719 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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

## Current Skill (Q=0.224) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
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
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: descend_1
- id: grasp
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_1
- id: lift
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
    - 0.1
    tolerance: 0.02
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release
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
- id: retract
  type: retract
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
    tolerance: 0.02
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.224
- **task_score** (E): 0.416
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2541 |
| descend | 1.00 | 1.00 | 0.0044 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1463 |
| transport | 1.00 | 1.00 | 0.1946 |
| place | 1.00 | 1.00 | 0.0160 |
| release | 1.00 | 1.00 | 0.0208 |
| retract | 1.00 | 1.00 | 0.0172 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.049) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.049)→(0.508, 0.017, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.503, 0.016, 0.039)→(0.503, 0.016, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.667 | 0.180 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.503, 0.016, 0.039)→(0.499, 0.016, 0.185) | (0.516, 0.017, 0.025)→(0.511, 0.017, 0.169) | 0.237→0.199 | 1.00 / 38.667 | 75.385 | 0.561 |
| transport | approach | 1.00 / step_budget | (0.499, 0.016, 0.185)→(0.597, 0.169, 0.230) | (0.511, 0.017, 0.169)→(0.599, 0.171, 0.206) | 0.199→0.041 | 1.00 / 38.667 | 108.440 | 0.320 |
| place | descend | 1.00 / step_budget | (0.597, 0.169, 0.230)→(0.598, 0.172, 0.214) | (0.599, 0.171, 0.206)→(0.601, 0.174, 0.190) | 0.041→0.025 | 1.00 / 39.000 | 0.088 | 0.337 |
| release | release | 1.00 / step_budget | (0.598, 0.172, 0.214)→(0.593, 0.170, 0.234) | (0.601, 0.174, 0.190)→(0.591, 0.169, 0.019) | 0.025→0.149 | 1.00 / 3.333 | 0.212 | 1.524 |
| retract | retract | 1.00 / step_budget | (0.593, 0.170, 0.234)→(0.598, 0.175, 0.249) | (0.591, 0.169, 0.019)→(0.594, 0.171, 0.027) | 0.149→0.142 | 1.00 / 3.333 | 0.160 | 0.230 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.568
- phase_score: 0.477
- phase_breakdown.approach_1_score: 0.675
- phase_breakdown.descend_1_score: 0.805
- phase_breakdown.transport_arc_score: 0.261
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.460
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.568
- **Median Q (composite search score)**: 0.240
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.397


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94245,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15432,"descend.descend_force_threshold":6.66665,"lift.lift_height":0.14906,"place.place_speed":0.12927,"place.place_z_offset":0.02008,"retract.retract_speed":0.1434,"transport.arc_height":0.07999,"transport.transport_speed":0.15571},"optimized_scores":{"best_composite_score":0.29888,"best_fitness_score":0.75388,"best_task_score":0.56835},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.5824,0.17027,-0.00463],"force_p95":0.93501,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13655,"mean_force":0.24748,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58857,0.17193,0.15523]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.52758,0.02731,-0.00157],"force_p95":0.49658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57561,"mean_force":0.11187,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51515,0.02752,0.04002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7120.0,"contact_point_centroid":[0.51326,0.04659,0.1053],"force_p95":0.0872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36921,"mean_force":0.06234,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51266,0.02737,0.10256]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.59043,0.19063,0.1646],"force_p95":0.10657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31762,"mean_force":0.06128,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.59406,0.17196,0.16075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1058.0,"contact_point_centroid":[0.58868,0.19185,0.14461],"force_p95":0.08971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31181,"mean_force":0.05421,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59263,0.17321,0.14103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8923.0,"contact_point_centroid":[0.51408,0.00842,0.10242],"force_p95":0.08138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30956,"mean_force":0.05138,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51268,0.02737,0.10058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9214.0,"contact_point_centroid":[0.54597,0.1087,0.21375],"force_p95":0.10967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27706,"mean_force":0.06434,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54707,0.08963,0.21116]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10838.0,"contact_point_centroid":[0.55209,0.07352,0.21261],"force_p95":0.08515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27315,"mean_force":0.05212,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54844,0.09194,0.21128]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5307,0.0306,-0.00232],"force_p95":0.19548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2603,"mean_force":0.14508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.517,0.02765,0.03889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.59712,0.15456,0.14117],"force_p95":0.08825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25641,"mean_force":0.0458,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59265,0.17322,0.14105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1222.0,"contact_point_centroid":[0.59824,0.15328,0.16101],"force_p95":0.10252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24379,"mean_force":0.05489,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.59404,0.17194,0.16093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6334.0,"contact_point_centroid":[0.51753,0.00865,0.04028],"force_p95":0.06898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15465,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02761,0.03832]},{"body_a":"world","body_b":"grasp_target","contact_count":456.0,"contact_point_centroid":[0.58211,0.17021,-0.00192],"force_p95":0.14528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.147,"mean_force":0.1219,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59122,0.17375,0.17702]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51081,0.0136,0.17502]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52248,0.02787,0.04605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.51737,0.04705,0.04118],"force_p95":0.09225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09515,"mean_force":0.05465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51651,0.02761,0.03833]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5821,0.17021,0.02602],"final_tcp_position":[0.59489,0.17585,0.18966],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":325.14019,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52353,0.02779,0.04814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52176,0.02793,0.04431],"tcp_start":[0.52353,0.02779,0.04814],"tcp_to_object_dist_end":0.02047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.02885,0.02507],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18612,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13080.0,"raw_peak_contact_force":0.2603,"subtask_id":"grasp_1","tcp_end":[0.51648,0.02761,0.03829],"tcp_start":[0.51648,0.02761,0.03829],"tcp_to_object_dist_end":0.01938,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":423.0,"n_steps_budget":930.0,"object_pos_end":[0.52558,0.02825,0.15138],"object_pos_start":[0.53061,0.02882,0.02512],"object_to_goal_dist_end":0.1739,"object_to_goal_dist_start":0.18532,"object_z_max":0.15111,"peak_contact_force":0.08362,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16129.0,"raw_peak_contact_force":0.57561,"tcp_end":[0.51286,0.02738,0.16775],"tcp_start":[0.51648,0.02761,0.03829],"tcp_to_object_dist_end":0.02075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.60131,0.17319,0.15308],"object_pos_start":[0.52558,0.02825,0.15138],"object_to_goal_dist_end":0.04531,"object_to_goal_dist_start":0.1739,"object_z_max":0.21566,"peak_contact_force":325.14019,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20052.0,"raw_peak_contact_force":0.27706,"subtask_id":"transport_arc","tcp_end":[0.59403,0.17045,0.1744],"tcp_start":[0.51286,0.02738,0.16775],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.603,0.17691,0.12408],"object_pos_start":[0.60131,0.17319,0.15308],"object_to_goal_dist_end":0.01615,"object_to_goal_dist_start":0.04531,"object_z_max":0.15308,"peak_contact_force":0.07857,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2258.0,"raw_peak_contact_force":0.31762,"subtask_id":"release_1","tcp_end":[0.59514,0.17383,0.14605],"tcp_start":[0.59403,0.17045,0.1744],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58322,0.1705,0.02651],"object_pos_start":[0.603,0.17691,0.12408],"object_to_goal_dist_end":0.084,"object_to_goal_dist_start":0.01615,"object_z_max":0.12408,"peak_contact_force":0.12527,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2654.0,"raw_peak_contact_force":1.13655,"tcp_end":[0.58847,0.17191,0.16594],"tcp_start":[0.59514,0.17383,0.14605],"tcp_to_object_dist_end":0.13954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.5821,0.17021,0.02602],"object_pos_start":[0.58322,0.1705,0.02651],"object_to_goal_dist_end":0.08475,"object_to_goal_dist_start":0.084,"object_z_max":0.0266,"peak_contact_force":0.12488,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":456.0,"raw_peak_contact_force":0.147,"tcp_end":[0.59489,0.17585,0.18966],"tcp_start":[0.58847,0.17191,0.16594],"tcp_to_object_dist_end":0.16424,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72441,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.29927,"descend.descend_force_threshold":9.2722,"lift.lift_height":0.16016,"place.place_speed":0.14338,"place.place_z_offset":0.04203,"retract.retract_speed":0.21109,"transport.arc_height":0.09091,"transport.transport_speed":0.21283},"optimized_scores":{"best_composite_score":0.13216,"best_fitness_score":0.58716,"best_task_score":0.23095},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.56675,0.17018,-0.01109],"force_p95":1.82964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93404,"mean_force":0.75771,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57442,0.17257,0.31335]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50044,-0.0143,-0.00142],"force_p95":0.46862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5422,"mean_force":0.12558,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49082,-0.01435,0.0407]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.5772,0.17326,-0.0055],"force_p95":0.29941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41066,"mean_force":0.16653,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57713,0.17632,0.32369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1174.0,"contact_point_centroid":[0.57142,0.192,0.29653],"force_p95":0.076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36757,"mean_force":0.0489,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5767,0.1735,0.29377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.57121,0.19012,0.30342],"force_p95":0.15303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36099,"mean_force":0.06523,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.57714,0.17195,0.29987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13666.0,"contact_point_centroid":[0.52207,0.03399,0.28349],"force_p95":0.1004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33119,"mean_force":0.05825,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51943,0.05282,0.28157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8499.0,"contact_point_centroid":[0.48755,-0.03351,0.11318],"force_p95":0.07684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31575,"mean_force":0.05542,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48831,-0.01432,0.11081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9551.0,"contact_point_centroid":[0.4888,0.00475,0.10888],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30912,"mean_force":0.05036,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48832,-0.01432,0.10716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1445.0,"contact_point_centroid":[0.58051,0.15455,0.29494],"force_p95":0.06336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24791,"mean_force":0.03893,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5767,0.1735,0.29378]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13352.0,"contact_point_centroid":[0.51833,0.07003,0.28263],"force_p95":0.09392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24729,"mean_force":0.05708,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51862,0.05118,0.28045]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.58089,0.15291,0.3013],"force_p95":0.0951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22271,"mean_force":0.0551,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.57714,0.17195,0.29987]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50387,-0.01565,-0.00213],"force_p95":0.154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21101,"mean_force":0.13215,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49251,-0.01436,0.03981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49234,0.00473,0.04082],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13999,"mean_force":0.04128,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01435,0.03928]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49897,-0.00695,0.1756]},{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49788,-0.01432,0.04665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5374.0,"contact_point_centroid":[0.49131,-0.03364,0.04191],"force_p95":0.07676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07967,"mean_force":0.04939,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01435,0.03929]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58704,0.17467,0.02865],"final_tcp_position":[0.58046,0.18089,0.33045],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49907,-0.01423,0.04891],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":60.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49715,-0.01438,0.04481],"tcp_start":[0.49907,-0.01423,0.04891],"tcp_to_object_dist_end":0.01998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01499,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15108,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13565.0,"raw_peak_contact_force":0.21101,"subtask_id":"grasp_1","tcp_end":[0.492,-0.01435,0.03926],"tcp_start":[0.492,-0.01435,0.03926],"tcp_to_object_dist_end":0.01803,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.49946,-0.0147,0.16374],"object_pos_start":[0.50377,-0.01499,0.02563],"object_to_goal_dist_end":0.23586,"object_to_goal_dist_start":0.31208,"object_z_max":0.16346,"peak_contact_force":0.07142,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18127.0,"raw_peak_contact_force":0.5422,"tcp_end":[0.48856,-0.01431,0.17986],"tcp_start":[0.492,-0.01435,0.03926],"tcp_to_object_dist_end":0.01947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.58219,0.17303,0.27895],"object_pos_start":[0.49946,-0.0147,0.16374],"object_to_goal_dist_end":0.03437,"object_to_goal_dist_start":0.23586,"object_z_max":0.30571,"peak_contact_force":0.07043,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27018.0,"raw_peak_contact_force":0.33119,"subtask_id":"transport_arc","tcp_end":[0.57717,0.17082,0.30201],"tcp_start":[0.48856,-0.01431,0.17986],"tcp_to_object_dist_end":0.0237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.58342,0.1761,0.27429],"object_pos_start":[0.58219,0.17303,0.27895],"object_to_goal_dist_end":0.02874,"object_to_goal_dist_start":0.03437,"object_z_max":0.27895,"peak_contact_force":0.07466,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":900.0,"raw_peak_contact_force":0.36099,"subtask_id":"release_1","tcp_end":[0.57795,0.17354,0.29753],"tcp_start":[0.57717,0.17082,0.30201],"tcp_to_object_dist_end":0.02401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57792,0.17148,0.00723],"object_pos_start":[0.58342,0.1761,0.27429],"object_to_goal_dist_end":0.24158,"object_to_goal_dist_start":0.02874,"object_z_max":0.27429,"peak_contact_force":0.43674,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2725.0,"raw_peak_contact_force":1.93404,"tcp_end":[0.57439,0.17256,0.31856],"tcp_start":[0.57795,0.17354,0.29753],"tcp_to_object_dist_end":0.31135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":70.0,"n_steps_budget":600.0,"object_pos_end":[0.58704,0.17467,0.02865],"object_pos_start":[0.57792,0.17148,0.00723],"object_to_goal_dist_end":0.21984,"object_to_goal_dist_start":0.24158,"object_z_max":0.03044,"peak_contact_force":0.22439,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":140.0,"raw_peak_contact_force":0.41066,"tcp_end":[0.58046,0.18089,0.33045],"tcp_start":[0.57439,0.17256,0.31856],"tcp_to_object_dist_end":0.30193,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9927,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.18729,"descend.descend_force_threshold":7.63814,"lift.lift_height":0.18857,"place.place_speed":0.17539,"place.place_z_offset":0.03561,"retract.retract_speed":0.22545,"transport.arc_height":0.09394,"transport.transport_speed":0.20455},"optimized_scores":{"best_composite_score":0.23961,"best_fitness_score":0.69461,"best_task_score":0.44928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.61194,0.16665,-0.00711],"force_p95":0.97779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50073,"mean_force":0.34293,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61507,0.16663,0.20987]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50948,0.03528,-0.00168],"force_p95":0.49829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56433,"mean_force":0.11819,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49872,0.03552,0.04097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9137.0,"contact_point_centroid":[0.49626,0.05457,0.12551],"force_p95":0.08772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36418,"mean_force":0.0618,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49638,0.03535,0.12292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10217.0,"contact_point_centroid":[0.54999,0.07111,0.26035],"force_p95":0.09207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35102,"mean_force":0.05822,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54741,0.09007,0.25938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":961.0,"contact_point_centroid":[0.6135,0.18583,0.19263],"force_p95":0.13224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34789,"mean_force":0.07014,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61848,0.16769,0.1931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.62103,0.1489,0.19046],"force_p95":0.15311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33439,"mean_force":0.06841,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61847,0.16769,0.19308]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":510.0,"contact_point_centroid":[0.61448,0.18531,0.20658],"force_p95":0.13084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33267,"mean_force":0.06802,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.61984,0.16736,0.20603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":415.0,"contact_point_centroid":[0.62238,0.14859,0.20354],"force_p95":0.13893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31493,"mean_force":0.08564,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.61984,0.16737,0.206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10166.0,"contact_point_centroid":[0.55005,0.11425,0.26317],"force_p95":0.08348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29864,"mean_force":0.05609,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5526,0.0955,0.26092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11667.0,"contact_point_centroid":[0.49757,0.0164,0.12432],"force_p95":0.07952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29813,"mean_force":0.04974,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49639,0.03535,0.12265]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51277,0.03946,-0.00241],"force_p95":0.21428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27518,"mean_force":0.15114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03568,0.03972]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6311.0,"contact_point_centroid":[0.50102,0.01667,0.04058],"force_p95":0.07276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17921,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50006,0.03564,0.03917]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50281,0.01751,0.17548]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.61195,0.16658,-0.00197],"force_p95":0.13075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1313,"mean_force":0.10648,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61705,0.16776,0.22144]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.506,0.03593,0.04663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.50022,0.05513,0.04145],"force_p95":0.09511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09925,"mean_force":0.0551,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50007,0.03564,0.03919]}],"total_contact_groups":16},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61223,0.16662,0.02614],"final_tcp_position":[0.61987,0.16927,0.22701],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":225.99862,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50717,0.03581,0.04883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50523,0.03601,0.04485],"tcp_start":[0.50717,0.03581,0.04883],"tcp_to_object_dist_end":0.02053,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51269,0.0372,0.0248],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21439,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20246,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13077.0,"raw_peak_contact_force":0.27518,"subtask_id":"grasp_1","tcp_end":[0.50004,0.03564,0.03915],"tcp_start":[0.50004,0.03564,0.03915],"tcp_to_object_dist_end":0.0192,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.50817,0.03647,0.1904],"object_pos_start":[0.51271,0.03717,0.02486],"object_to_goal_dist_end":0.18662,"object_to_goal_dist_start":0.21436,"object_z_max":0.19012,"peak_contact_force":225.99862,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20889.0,"raw_peak_contact_force":0.56433,"tcp_end":[0.49683,0.03538,0.20799],"tcp_start":[0.50004,0.03564,0.03915],"tcp_to_object_dist_end":0.02095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.61411,0.16709,0.18708],"object_pos_start":[0.50817,0.03647,0.1904],"object_to_goal_dist_end":0.04449,"object_to_goal_dist_start":0.18662,"object_z_max":0.2653,"peak_contact_force":0.11024,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20383.0,"raw_peak_contact_force":0.35102,"subtask_id":"transport_arc","tcp_end":[0.62011,0.16694,0.21251],"tcp_start":[0.49683,0.03538,0.20799],"tcp_to_object_dist_end":0.02613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":30.0,"n_steps_budget":1000.0,"object_pos_end":[0.61629,0.16898,0.17291],"object_pos_start":[0.61411,0.16709,0.18708],"object_to_goal_dist_end":0.03028,"object_to_goal_dist_start":0.04449,"object_z_max":0.18708,"peak_contact_force":0.11203,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":925.0,"raw_peak_contact_force":0.33267,"subtask_id":"release_1","tcp_end":[0.62074,0.16825,0.1986],"tcp_start":[0.62011,0.16694,0.21251],"tcp_to_object_dist_end":0.02608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61057,0.16632,0.02348],"object_pos_start":[0.61629,0.16898,0.17291],"object_to_goal_dist_end":0.12288,"object_to_goal_dist_start":0.03028,"object_z_max":0.17291,"peak_contact_force":0.07473,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2114.0,"raw_peak_contact_force":1.50073,"tcp_end":[0.61502,0.16662,0.21753],"tcp_start":[0.62074,0.16825,0.1986],"tcp_to_object_dist_end":0.1941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":600.0,"object_pos_end":[0.61223,0.16662,0.02614],"object_pos_start":[0.61057,0.16632,0.02348],"object_to_goal_dist_end":0.12002,"object_to_goal_dist_start":0.12288,"object_z_max":0.02661,"peak_contact_force":0.13035,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":240.0,"raw_peak_contact_force":0.1313,"tcp_end":[0.61987,0.16927,0.22701],"tcp_start":[0.61502,0.16662,0.21753],"tcp_to_object_dist_end":0.20104,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```