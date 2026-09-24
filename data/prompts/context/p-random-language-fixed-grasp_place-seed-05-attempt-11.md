## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2228 | 0.42 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.2227 | 0.41 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3481 | 0.42 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2235 | 0.42 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3719 | 0.42 | ✅ accepted |

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

## Current Skill (Q=0.223) — your mutation base

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

- **Composite score**: 0.223
- **task_score** (E): 0.416
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2542 |
| descend | 1.00 | 1.00 | 0.0033 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1494 |
| transport | 1.00 | 1.00 | 0.1960 |
| place_descend | 1.00 | 1.00 | 0.0697 |
| release | 1.00 | 1.00 | 0.0218 |
| retract | 1.00 | 1.00 | 0.0663 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.049) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.049)→(0.509, 0.017, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 118.200 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.503, 0.016, 0.040)→(0.503, 0.016, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.667 | 0.180 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.503, 0.016, 0.040)→(0.500, 0.016, 0.189) | (0.516, 0.017, 0.025)→(0.511, 0.017, 0.172) | 0.237→0.202 | 1.00 / 39.667 | 0.079 | 0.557 |
| transport | approach | 1.00 / step_budget | (0.500, 0.016, 0.189)→(0.597, 0.169, 0.230) | (0.511, 0.017, 0.172)→(0.596, 0.170, 0.206) | 0.202→0.042 | 1.00 / 37.000 | 0.083 | 0.275 |
| place_descend | descend | 1.00 / step_budget | (0.597, 0.169, 0.230)→(0.601, 0.178, 0.161) | (0.596, 0.170, 0.206)→(0.600, 0.180, 0.133) | 0.042→0.034 | 1.00 / 28.000 | 0.099 | 0.336 |
| release | release | 1.00 / step_budget | (0.601, 0.178, 0.161)→(0.595, 0.176, 0.182) | (0.600, 0.180, 0.133)→(0.592, 0.176, 0.024) | 0.034→0.144 | 1.00 / 4.000 | 0.127 | 1.360 |
| retract | retract | 1.00 / step_budget | (0.595, 0.176, 0.182)→(0.601, 0.178, 0.248) | (0.592, 0.176, 0.024)→(0.592, 0.175, 0.026) | 0.144→0.142 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.569
- phase_score: 0.508
- phase_breakdown.approach_1_score: 0.675
- phase_breakdown.descend_1_score: 0.805
- phase_breakdown.transport_arc_score: 0.257
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.679
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.569
- **Median Q (composite search score)**: 0.241
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17483,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15367,"descend.descend_force_threshold":4.68682,"grasp.bilateral_threshold":0.00959,"lift.lift_height":0.18683,"place_descend.place_tolerance":0.0055,"retract.retract_speed":0.12465,"transport.arc_height":0.071,"transport.transport_speed":0.24827},"optimized_scores":{"best_composite_score":0.29941,"best_fitness_score":0.75441,"best_task_score":0.56942},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":370.0,"contact_point_centroid":[0.58246,0.1744,-0.00334],"force_p95":0.53523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96403,"mean_force":0.186,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58992,0.17506,0.10972]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.52759,0.02731,-0.00158],"force_p95":0.49517,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57487,"mean_force":0.11084,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51516,0.02752,0.04001]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9279.0,"contact_point_centroid":[0.51331,0.04658,0.12436],"force_p95":0.08617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36885,"mean_force":0.06167,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51273,0.02737,0.12163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11462.0,"contact_point_centroid":[0.51426,0.00843,0.12094],"force_p95":0.0811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30909,"mean_force":0.05148,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51274,0.02737,0.11916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9783.0,"contact_point_centroid":[0.55708,0.08127,0.22755],"force_p95":0.0828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27732,"mean_force":0.05161,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55364,0.10011,0.22603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15881.0,"contact_point_centroid":[0.58979,0.19288,0.13207],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26428,"mean_force":0.04918,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59449,0.1745,0.12871]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5307,0.0306,-0.00232],"force_p95":0.19548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2603,"mean_force":0.14508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.517,0.02765,0.03889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17343.0,"contact_point_centroid":[0.59884,0.15582,0.12838],"force_p95":0.06788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2334,"mean_force":0.04641,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59455,0.17457,0.12791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8775.0,"contact_point_centroid":[0.55272,0.12141,0.2287],"force_p95":0.08226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22294,"mean_force":0.05506,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55505,0.10254,0.22552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6334.0,"contact_point_centroid":[0.51753,0.00865,0.04028],"force_p95":0.06898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15465,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02761,0.03832]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51081,0.0136,0.17502]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.58199,0.17437,-0.00199],"force_p95":0.12504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13021,"mean_force":0.12274,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59209,0.17573,0.15552]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52248,0.02787,0.04605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.59921,0.15795,0.09796],"force_p95":0.07185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11352,"mean_force":0.04228,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59466,0.17648,0.09867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1049.0,"contact_point_centroid":[0.59101,0.1952,0.10118],"force_p95":0.08129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10735,"mean_force":0.0477,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59466,0.17648,0.09867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.51737,0.04705,0.04118],"force_p95":0.09225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09515,"mean_force":0.05465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51651,0.02761,0.03833]}],"total_contact_groups":16},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58199,0.17437,0.02602],"final_tcp_position":[0.59649,0.17705,0.1888],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52353,0.02779,0.04814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52176,0.02793,0.04431],"tcp_start":[0.52353,0.02779,0.04814],"tcp_to_object_dist_end":0.02047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.02885,0.02507],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18612,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13080.0,"raw_peak_contact_force":0.2603,"subtask_id":"grasp_1","tcp_end":[0.51648,0.02761,0.03829],"tcp_start":[0.51648,0.02761,0.03829],"tcp_to_object_dist_end":0.01938,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.52545,0.02826,0.18841],"object_pos_start":[0.53061,0.02882,0.02512],"object_to_goal_dist_end":0.18665,"object_to_goal_dist_start":0.18532,"object_z_max":0.18814,"peak_contact_force":0.0825,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20827.0,"raw_peak_contact_force":0.57487,"tcp_end":[0.51321,0.0274,0.2056],"tcp_start":[0.51648,0.02761,0.03829],"tcp_to_object_dist_end":0.02113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.59604,0.1733,0.15476],"object_pos_start":[0.52545,0.02826,0.18841],"object_to_goal_dist_end":0.04729,"object_to_goal_dist_start":0.18665,"object_z_max":0.22617,"peak_contact_force":0.06941,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18558.0,"raw_peak_contact_force":0.27732,"subtask_id":"transport_arc","tcp_end":[0.59472,0.17164,0.17524],"tcp_start":[0.51321,0.0274,0.2056],"tcp_to_object_dist_end":0.02059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.59558,0.17856,0.07856],"object_pos_start":[0.59604,0.1733,0.15476],"object_to_goal_dist_end":0.03012,"object_to_goal_dist_start":0.04729,"object_z_max":0.15476,"peak_contact_force":0.08137,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33224.0,"raw_peak_contact_force":0.26428,"tcp_end":[0.59662,0.17703,0.10197],"tcp_start":[0.59472,0.17164,0.17524],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58157,0.17431,0.02622],"object_pos_start":[0.59558,0.17856,0.07856],"object_to_goal_dist_end":0.08437,"object_to_goal_dist_start":0.03012,"object_z_max":0.07856,"peak_contact_force":0.13029,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2655.0,"raw_peak_contact_force":0.96403,"subtask_id":"release_1","tcp_end":[0.58974,0.175,0.12305],"tcp_start":[0.59662,0.17703,0.10197],"tcp_to_object_dist_end":0.09717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.58199,0.17437,0.02602],"object_pos_start":[0.58157,0.17431,0.02622],"object_to_goal_dist_end":0.08447,"object_to_goal_dist_start":0.08437,"object_z_max":0.02622,"peak_contact_force":0.12264,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.13021,"tcp_end":[0.59649,0.17705,0.1888],"tcp_start":[0.58974,0.175,0.12305],"tcp_to_object_dist_end":0.16344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94872,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.20134,"descend.descend_force_threshold":8.55647,"grasp.bilateral_threshold":0.01331,"lift.lift_height":0.15492,"place_descend.place_tolerance":0.00517,"retract.retract_speed":0.1783,"transport.arc_height":0.09072,"transport.transport_speed":0.09809},"optimized_scores":{"best_composite_score":0.12803,"best_fitness_score":0.58303,"best_task_score":0.22675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.57521,0.17841,-0.00881],"force_p95":1.16736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.954,"mean_force":0.44156,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5791,0.18437,0.25698]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50069,-0.01401,-0.00143],"force_p95":0.46049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52669,"mean_force":0.11931,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49207,-0.01427,0.04333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7979.0,"contact_point_centroid":[0.57532,0.19811,0.26318],"force_p95":0.10298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39866,"mean_force":0.07023,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58032,0.17984,0.26342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.48848,-0.03344,0.11351],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30808,"mean_force":0.05291,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48957,-0.01424,0.11166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9421.0,"contact_point_centroid":[0.4897,0.00488,0.11026],"force_p95":0.07245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30176,"mean_force":0.04903,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48958,-0.01424,0.10895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9359.0,"contact_point_centroid":[0.58433,0.1617,0.2611],"force_p95":0.09486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27815,"mean_force":0.06112,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58034,0.17988,0.26326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16592.0,"contact_point_centroid":[0.51381,0.0617,0.27807],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21581,"mean_force":0.05261,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51509,0.04262,0.27562]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50387,-0.01565,-0.00213],"force_p95":0.15413,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21131,"mean_force":0.1323,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4937,-0.01428,0.04238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17796.0,"contact_point_centroid":[0.5179,0.02691,0.28024],"force_p95":0.07313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1982,"mean_force":0.04977,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51668,0.0459,0.27817]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.57511,0.17868,-0.00206],"force_p95":0.13442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1438,"mean_force":0.11614,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58083,0.18513,0.29528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49337,0.00481,0.04317],"force_p95":0.06579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14187,"mean_force":0.0413,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49328,-0.01427,0.04192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.57822,0.20392,0.23736],"force_p95":0.09989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13905,"mean_force":0.06351,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58208,0.18545,0.23889]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49898,-0.00697,0.17538]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49904,-0.01426,0.0485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.58694,0.16756,0.23429],"force_p95":0.10458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11033,"mean_force":0.06652,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.582,0.18542,0.23873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5379.0,"contact_point_centroid":[0.49196,-0.03355,0.04431],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07966,"mean_force":0.04938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49328,-0.01427,0.04192]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57511,0.17869,0.02602],"final_tcp_position":[0.58389,0.18632,0.3284],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":192.31669,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49925,-0.01424,0.04896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":192.31669,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49857,-0.01429,0.04766],"tcp_start":[0.49925,-0.01424,0.04896],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50379,-0.01497,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15097,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13570.0,"raw_peak_contact_force":0.21131,"subtask_id":"grasp_1","tcp_end":[0.49326,-0.01427,0.0419],"tcp_start":[0.49326,-0.01427,0.0419],"tcp_to_object_dist_end":0.01941,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":431.0,"n_steps_budget":960.0,"object_pos_end":[0.49992,-0.01465,0.15885],"object_pos_start":[0.50379,-0.01497,0.02562],"object_to_goal_dist_end":0.23744,"object_to_goal_dist_start":0.31207,"object_z_max":0.15857,"peak_contact_force":0.06938,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18107.0,"raw_peak_contact_force":0.52669,"tcp_end":[0.48979,-0.01423,0.17715],"tcp_start":[0.49326,-0.01427,0.0419],"tcp_to_object_dist_end":0.02092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.57852,0.17211,0.27774],"object_pos_start":[0.49992,-0.01465,0.15885],"object_to_goal_dist_end":0.0344,"object_to_goal_dist_start":0.23744,"object_z_max":0.3037,"peak_contact_force":0.08701,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34388.0,"raw_peak_contact_force":0.21581,"subtask_id":"transport_arc","tcp_end":[0.57729,0.17069,0.30266],"tcp_start":[0.48979,-0.01423,0.17715],"tcp_to_object_dist_end":0.02499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.58318,0.18704,0.21325],"object_pos_start":[0.57852,0.17211,0.27774],"object_to_goal_dist_end":0.03506,"object_to_goal_dist_start":0.0344,"object_z_max":0.27774,"peak_contact_force":0.10122,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17338.0,"raw_peak_contact_force":0.39866,"tcp_end":[0.58343,0.18586,0.2422],"tcp_start":[0.57729,0.17069,0.30266],"tcp_to_object_dist_end":0.02897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57513,0.18277,0.01934],"object_pos_start":[0.58318,0.18704,0.21325],"object_to_goal_dist_end":0.22913,"object_to_goal_dist_start":0.03506,"object_z_max":0.21325,"peak_contact_force":0.12173,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1690.0,"raw_peak_contact_force":1.954,"subtask_id":"release_1","tcp_end":[0.57907,0.18436,0.26347],"tcp_start":[0.58343,0.18586,0.2422],"tcp_to_object_dist_end":0.24417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":600.0,"object_pos_end":[0.57511,0.17869,0.02602],"object_pos_start":[0.57513,0.18277,0.01934],"object_to_goal_dist_end":0.22258,"object_to_goal_dist_start":0.22913,"object_z_max":0.02676,"peak_contact_force":0.12279,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":980.0,"raw_peak_contact_force":0.1438,"tcp_end":[0.58389,0.18632,0.3284],"tcp_start":[0.57907,0.18436,0.26347],"tcp_to_object_dist_end":0.30261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28058,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15467,"descend.descend_force_threshold":4.94813,"grasp.bilateral_threshold":0.0072,"lift.lift_height":0.16508,"place_descend.place_tolerance":0.00323,"retract.retract_speed":0.23555,"transport.arc_height":0.09323,"transport.transport_speed":0.27779},"optimized_scores":{"best_composite_score":0.2411,"best_fitness_score":0.6961,"best_task_score":0.45165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":307.0,"contact_point_centroid":[0.6202,0.17136,-0.00424],"force_p95":0.71116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16291,"mean_force":0.22075,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61668,0.16933,0.14719]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.50959,0.03544,-0.00162],"force_p95":0.46518,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56959,"mean_force":0.11429,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49881,0.03556,0.04091]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7941.0,"contact_point_centroid":[0.49632,0.05461,0.11346],"force_p95":0.08872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35912,"mean_force":0.06188,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49644,0.03539,0.11093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9961.0,"contact_point_centroid":[0.61553,0.18638,0.16545],"force_p95":0.10254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34601,"mean_force":0.07185,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61967,0.16818,0.16609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10687.0,"contact_point_centroid":[0.54523,0.06642,0.24543],"force_p95":0.09141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33279,"mean_force":0.05724,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5427,0.08538,0.24429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9494.0,"contact_point_centroid":[0.6233,0.15015,0.16086],"force_p95":0.10629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30276,"mean_force":0.07737,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61987,0.16835,0.16448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10095.0,"contact_point_centroid":[0.49761,0.01644,0.11183],"force_p95":0.08082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29711,"mean_force":0.04999,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49644,0.03539,0.11029]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51277,0.03946,-0.00241],"force_p95":0.21354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27459,"mean_force":0.15088,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50066,0.03572,0.03956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10455.0,"contact_point_centroid":[0.54651,0.11055,0.24891],"force_p95":0.08352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27367,"mean_force":0.05601,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5488,0.09175,0.24651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6312.0,"contact_point_centroid":[0.50111,0.01671,0.04039],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17991,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50017,0.03568,0.03901]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.62037,0.17135,-0.00197],"force_p95":0.13273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14056,"mean_force":0.12255,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61888,0.16999,0.19165]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50278,0.01755,0.17516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":634.0,"contact_point_centroid":[0.61841,0.18944,0.13352],"force_p95":0.1131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13827,"mean_force":0.07647,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62103,0.1706,0.13467]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5061,0.03598,0.04638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":801.0,"contact_point_centroid":[0.62525,0.15291,0.12986],"force_p95":0.09586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11851,"mean_force":0.06295,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62104,0.1706,0.13468]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.50029,0.05517,0.04125],"force_p95":0.095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09913,"mean_force":0.05518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50018,0.03568,0.03902]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62038,0.17136,0.02602],"final_tcp_position":[0.62309,0.1712,0.22565],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5072,0.03587,0.04842],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.50534,0.03606,0.04469],"tcp_start":[0.5072,0.03587,0.04842],"tcp_to_object_dist_end":0.02033,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51269,0.03722,0.02481],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21437,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20179,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13068.0,"raw_peak_contact_force":0.27459,"subtask_id":"grasp_1","tcp_end":[0.50014,0.03568,0.03899],"tcp_start":[0.50014,0.03568,0.03899],"tcp_to_object_dist_end":0.01899,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.5081,0.03654,0.16745],"object_pos_start":[0.5127,0.03719,0.02487],"object_to_goal_dist_end":0.18239,"object_to_goal_dist_start":0.21435,"object_z_max":0.16717,"peak_contact_force":0.08441,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18125.0,"raw_peak_contact_force":0.56959,"tcp_end":[0.49672,0.03541,0.18447],"tcp_start":[0.50014,0.03568,0.03899],"tcp_to_object_dist_end":0.02051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.61231,0.16496,0.18602],"object_pos_start":[0.5081,0.03654,0.16745],"object_to_goal_dist_end":0.04439,"object_to_goal_dist_start":0.18239,"object_z_max":0.25303,"peak_contact_force":0.09388,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21142.0,"raw_peak_contact_force":0.33279,"subtask_id":"transport_arc","tcp_end":[0.61817,0.16493,0.21076],"tcp_start":[0.49672,0.03541,0.18447],"tcp_to_object_dist_end":0.02543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.62139,0.17332,0.10765],"object_pos_start":[0.61231,0.16496,0.18602],"object_to_goal_dist_end":0.03789,"object_to_goal_dist_start":0.04439,"object_z_max":0.18602,"peak_contact_force":0.11396,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19455.0,"raw_peak_contact_force":0.34601,"tcp_end":[0.62293,0.17111,0.13832],"tcp_start":[0.61817,0.16493,0.21076],"tcp_to_object_dist_end":0.03079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62011,0.17117,0.02646],"object_pos_start":[0.62139,0.17332,0.10765],"object_to_goal_dist_end":0.11881,"object_to_goal_dist_start":0.03789,"object_z_max":0.10765,"peak_contact_force":0.13043,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1742.0,"raw_peak_contact_force":1.16291,"subtask_id":"release_1","tcp_end":[0.61657,0.1693,0.1585],"tcp_start":[0.62293,0.17111,0.13832],"tcp_to_object_dist_end":0.1321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":600.0,"object_pos_end":[0.62038,0.17136,0.02602],"object_pos_start":[0.62011,0.17117,0.02646],"object_to_goal_dist_end":0.11923,"object_to_goal_dist_start":0.11881,"object_z_max":0.02647,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.14056,"tcp_end":[0.62309,0.1712,0.22565],"tcp_start":[0.61657,0.1693,0.1585],"tcp_to_object_dist_end":0.19965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```