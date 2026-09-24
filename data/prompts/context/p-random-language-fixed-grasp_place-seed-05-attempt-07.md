## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3719 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

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

## Current Skill (Q=0.372) — your mutation base

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

- **Composite score**: 0.372
- **task_score** (E): 0.418
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2542 |
| descend | 1.00 | 1.00 | 0.0033 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1636 |
| transport | 1.00 | 1.00 | 0.1990 |
| release | 1.00 | 1.00 | 0.0206 |
| retract | 1.00 | 1.00 | 0.0057 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.048) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.048)→(0.509, 0.017, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 118.200 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.503, 0.016, 0.040)→(0.503, 0.016, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.667 | 0.180 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.503, 0.016, 0.040)→(0.500, 0.016, 0.203) | (0.516, 0.017, 0.025)→(0.511, 0.017, 0.186) | 0.237→0.207 | 1.00 / 39.000 | 73.139 | 0.557 |
| transport | approach | 1.00 / step_budget | (0.500, 0.016, 0.203)→(0.598, 0.171, 0.230) | (0.511, 0.017, 0.186)→(0.603, 0.174, 0.208) | 0.207→0.042 | 1.00 / 41.667 | 0.075 | 0.251 |
| release | release | 1.00 / step_budget | (0.598, 0.171, 0.230)→(0.593, 0.170, 0.250) | (0.603, 0.174, 0.208)→(0.592, 0.169, 0.019) | 0.042→0.150 | 1.00 / 2.667 | 0.248 | 1.626 |
| retract | retract | 1.00 / step_budget | (0.593, 0.170, 0.250)→(0.596, 0.173, 0.253) | (0.592, 0.169, 0.019)→(0.592, 0.168, 0.028) | 0.150→0.141 | 1.00 / 2.667 | 0.169 | 0.254 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.571
- phase_score: 0.426
- phase_breakdown.approach_1_score: 0.675
- phase_breakdown.descend_1_score: 0.805
- phase_breakdown.transport_arc_score: 0.248
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.166
- grasp_place_fitness: 0.755

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.755
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.571
- **Median Q (composite search score)**: 0.389
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15495,"descend.descend_force_threshold":7.43749,"lift.lift_height":0.19961,"retract.retract_speed":0.16261,"transport.arc_height":0.09777,"transport.transport_speed":0.26943},"optimized_scores":{"best_composite_score":0.44829,"best_fitness_score":0.75544,"best_task_score":0.57147},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.58251,0.17174,-0.00585],"force_p95":0.92268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33059,"mean_force":0.28572,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5915,0.17468,0.1878]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.52732,0.02751,-0.00159],"force_p95":0.49928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57591,"mean_force":0.11363,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51516,0.02752,0.04]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9874.0,"contact_point_centroid":[0.51334,0.04658,0.13047],"force_p95":0.08601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36937,"mean_force":0.06158,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51277,0.02737,0.12774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12165.0,"contact_point_centroid":[0.51432,0.00843,0.12693],"force_p95":0.0811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30976,"mean_force":0.05154,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51278,0.02737,0.12515]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10704.0,"contact_point_centroid":[0.56031,0.08639,0.24448],"force_p95":0.08407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30874,"mean_force":0.0514,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55668,0.105,0.24297]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5307,0.0306,-0.00232],"force_p95":0.19548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2603,"mean_force":0.14508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.517,0.02765,0.03889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9257.0,"contact_point_centroid":[0.55511,0.12479,0.24486],"force_p95":0.10459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24704,"mean_force":0.06092,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5572,0.10591,0.24179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1270.0,"contact_point_centroid":[0.58998,0.19415,0.17589],"force_p95":0.0741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22033,"mean_force":0.04328,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5952,0.17586,0.17229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1341.0,"contact_point_centroid":[0.59973,0.15701,0.1731],"force_p95":0.07481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21314,"mean_force":0.0421,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59519,0.17586,0.17227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6334.0,"contact_point_centroid":[0.51753,0.00865,0.04028],"force_p95":0.06898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15465,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02761,0.03832]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51081,0.0136,0.17502]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5825,0.17176,-0.0018],"force_p95":0.13077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13333,"mean_force":0.10265,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59171,0.17483,0.19731]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52248,0.02787,0.04605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.51737,0.04705,0.04118],"force_p95":0.09225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09515,"mean_force":0.05465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51651,0.02761,0.03833]}],"total_contact_groups":14},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58257,0.17179,0.02661],"final_tcp_position":[0.59216,0.17507,0.19707],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52353,0.02779,0.04814],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52176,0.02793,0.04431],"tcp_start":[0.52353,0.02779,0.04814],"tcp_to_object_dist_end":0.02047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.02885,0.02507],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18612,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13080.0,"raw_peak_contact_force":0.2603,"subtask_id":"grasp_1","tcp_end":[0.51648,0.02761,0.03829],"tcp_start":[0.51648,0.02761,0.03829],"tcp_to_object_dist_end":0.01938,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.52551,0.02826,0.2008],"object_pos_start":[0.53061,0.02882,0.02512],"object_to_goal_dist_end":0.19228,"object_to_goal_dist_start":0.18532,"object_z_max":0.20053,"peak_contact_force":0.08222,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22124.0,"raw_peak_contact_force":0.57591,"tcp_end":[0.51333,0.02741,0.21816],"tcp_start":[0.51648,0.02761,0.03829],"tcp_to_object_dist_end":0.02122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.59791,0.17785,0.15643],"object_pos_start":[0.52551,0.02826,0.2008],"object_to_goal_dist_end":0.04848,"object_to_goal_dist_start":0.19228,"object_z_max":0.24808,"peak_contact_force":0.07745,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19961.0,"raw_peak_contact_force":0.30874,"subtask_id":"transport_arc","tcp_end":[0.59756,0.17655,0.17758],"tcp_start":[0.51333,0.02741,0.21816],"tcp_to_object_dist_end":0.02119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58416,0.17237,0.0258],"object_pos_start":[0.59791,0.17785,0.15643],"object_to_goal_dist_end":0.08433,"object_to_goal_dist_start":0.04848,"object_z_max":0.15643,"peak_contact_force":0.09284,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2859.0,"raw_peak_contact_force":1.33059,"subtask_id":"release_1","tcp_end":[0.59143,0.17466,0.19713],"tcp_start":[0.59756,0.17655,0.17758],"tcp_to_object_dist_end":0.1715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.58257,0.17179,0.02661],"object_pos_start":[0.58416,0.17237,0.0258],"object_to_goal_dist_end":0.08393,"object_to_goal_dist_start":0.08433,"object_z_max":0.02662,"peak_contact_force":0.13333,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":0.13333,"tcp_end":[0.59216,0.17507,0.19707],"tcp_start":[0.59143,0.17466,0.19713],"tcp_to_object_dist_end":0.17076,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16667,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.20431,"descend.descend_force_threshold":5.4593,"lift.lift_height":0.14976,"retract.retract_speed":0.26569,"transport.arc_height":0.0884,"transport.transport_speed":0.17026},"optimized_scores":{"best_composite_score":0.27865,"best_fitness_score":0.58579,"best_task_score":0.23229},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.56583,0.16469,-0.01083],"force_p95":1.75492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98536,"mean_force":0.72023,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57363,0.16978,0.31748]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50069,-0.01401,-0.00144],"force_p95":0.46007,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52662,"mean_force":0.11919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49207,-0.01427,0.04333]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.57857,0.1663,-0.00594],"force_p95":0.34152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48217,"mean_force":0.16519,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57639,0.17393,0.3262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1178.0,"contact_point_centroid":[0.57049,0.18916,0.29954],"force_p95":0.07693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35974,"mean_force":0.04893,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57582,0.17075,0.29747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8258.0,"contact_point_centroid":[0.48847,-0.03344,0.11087],"force_p95":0.07688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30805,"mean_force":0.05315,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48957,-0.01424,0.109]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9073.0,"contact_point_centroid":[0.4897,0.00488,0.10775],"force_p95":0.07264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30172,"mean_force":0.04909,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48957,-0.01424,0.10645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15499.0,"contact_point_centroid":[0.52022,0.03009,0.2768],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27402,"mean_force":0.05235,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51824,0.04909,0.27484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1345.0,"contact_point_centroid":[0.58,0.15193,0.2977],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23706,"mean_force":0.04162,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57583,0.17076,0.29749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15191.0,"contact_point_centroid":[0.51675,0.06721,0.27587],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22024,"mean_force":0.05234,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51783,0.04821,0.2737]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50387,-0.01565,-0.00213],"force_p95":0.15413,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21131,"mean_force":0.1323,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4937,-0.01428,0.04238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49337,0.00481,0.04317],"force_p95":0.06579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14187,"mean_force":0.0413,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49328,-0.01427,0.04192]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49898,-0.00697,0.17538]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49904,-0.01426,0.0485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5379.0,"contact_point_centroid":[0.49196,-0.03355,0.04431],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07966,"mean_force":0.04938,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49328,-0.01427,0.04192]}],"total_contact_groups":14},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5844,0.17058,0.02982],"final_tcp_position":[0.57983,0.1792,0.3315],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":219.25053,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49925,-0.01424,0.04896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":192.31669,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49857,-0.01429,0.04766],"tcp_start":[0.49925,-0.01424,0.04896],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50379,-0.01497,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15097,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13570.0,"raw_peak_contact_force":0.21131,"subtask_id":"grasp_1","tcp_end":[0.49326,-0.01427,0.0419],"tcp_start":[0.49326,-0.01427,0.0419],"tcp_to_object_dist_end":0.01941,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":415.0,"n_steps_budget":930.0,"object_pos_end":[0.4999,-0.01466,0.15395],"object_pos_start":[0.50379,-0.01497,0.02562],"object_to_goal_dist_end":0.23934,"object_to_goal_dist_start":0.31207,"object_z_max":0.15367,"peak_contact_force":219.25053,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17407.0,"raw_peak_contact_force":0.52662,"tcp_end":[0.48976,-0.01423,0.17219],"tcp_start":[0.49326,-0.01427,0.0419],"tcp_to_object_dist_end":0.02088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.58401,0.17321,0.27673],"object_pos_start":[0.4999,-0.01466,0.15395],"object_to_goal_dist_end":0.0321,"object_to_goal_dist_start":0.23934,"object_z_max":0.29936,"peak_contact_force":0.07068,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30690.0,"raw_peak_contact_force":0.27402,"subtask_id":"transport_arc","tcp_end":[0.57714,0.17056,0.30121],"tcp_start":[0.48976,-0.01423,0.17219],"tcp_to_object_dist_end":0.02556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.577,0.1706,0.00653],"object_pos_start":[0.58401,0.17321,0.27673],"object_to_goal_dist_end":0.24238,"object_to_goal_dist_start":0.0321,"object_z_max":0.27673,"peak_contact_force":0.50912,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2634.0,"raw_peak_contact_force":1.98536,"subtask_id":"release_1","tcp_end":[0.5736,0.16978,0.32233],"tcp_start":[0.57714,0.17056,0.30121],"tcp_to_object_dist_end":0.31581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":63.0,"n_steps_budget":600.0,"object_pos_end":[0.5844,0.17058,0.02982],"object_pos_start":[0.577,0.1706,0.00653],"object_to_goal_dist_end":0.21897,"object_to_goal_dist_start":0.24238,"object_z_max":0.03041,"peak_contact_force":0.22664,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":126.0,"raw_peak_contact_force":0.48217,"tcp_end":[0.57983,0.1792,0.3315],"tcp_start":[0.5736,0.16978,0.32233],"tcp_to_object_dist_end":0.30185,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80925,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.21154,"descend.descend_force_threshold":7.10249,"lift.lift_height":0.1999,"retract.retract_speed":0.21836,"transport.arc_height":0.11446,"transport.transport_speed":0.05078},"optimized_scores":{"best_composite_score":0.38861,"best_fitness_score":0.69575,"best_task_score":0.45066},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.60628,0.16231,-0.00739],"force_p95":1.27072,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56265,"mean_force":0.37601,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61383,0.16464,0.22272]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50947,0.03528,-0.00167],"force_p95":0.50433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56973,"mean_force":0.11993,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49873,0.03558,0.0406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9825.0,"contact_point_centroid":[0.49627,0.05463,0.13099],"force_p95":0.08716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36483,"mean_force":0.06153,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49642,0.03541,0.12838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1109.0,"contact_point_centroid":[0.61312,0.18431,0.21065],"force_p95":0.0872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31428,"mean_force":0.05258,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61718,0.16572,0.20656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12500.0,"contact_point_centroid":[0.49762,0.01646,0.12956],"force_p95":0.07926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29931,"mean_force":0.04969,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49643,0.03541,0.12787]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51277,0.03946,-0.00241],"force_p95":0.21347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27467,"mean_force":0.15084,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50057,0.03574,0.03934]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1355.0,"contact_point_centroid":[0.62131,0.14694,0.2072],"force_p95":0.08044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24134,"mean_force":0.04467,"phase_index":5.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6172,0.16572,0.20659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6311.0,"contact_point_centroid":[0.50104,0.01672,0.0402],"force_p95":0.07257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18055,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50007,0.0357,0.0388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13623.0,"contact_point_centroid":[0.55685,0.078,0.25819],"force_p95":0.08539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17133,"mean_force":0.0512,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55344,0.09674,0.25679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11538.0,"contact_point_centroid":[0.55119,0.11528,0.26039],"force_p95":0.08949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15889,"mean_force":0.05884,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.553,0.09628,0.25709]},{"body_a":"world","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.62353,0.16724,-0.00396],"force_p95":0.14472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14795,"mean_force":0.12317,"phase_index":6.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61428,0.16494,0.23114]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50285,0.01756,0.17514]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50598,0.03598,0.04624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.50023,0.05518,0.04107],"force_p95":0.09501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09912,"mean_force":0.05514,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50008,0.0357,0.03881]}],"total_contact_groups":14},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60963,0.16291,0.02721],"final_tcp_position":[0.61525,0.16559,0.23118],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50713,0.03587,0.04838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50524,0.03607,0.04448],"tcp_start":[0.50713,0.03587,0.04838],"tcp_to_object_dist_end":0.02018,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51268,0.03722,0.02482],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21437,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20173,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13071.0,"raw_peak_contact_force":0.27467,"subtask_id":"grasp_1","tcp_end":[0.50005,0.03569,0.03877],"tcp_start":[0.50005,0.03569,0.03877],"tcp_to_object_dist_end":0.01889,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.50826,0.03645,0.20179],"object_pos_start":[0.5127,0.03719,0.02488],"object_to_goal_dist_end":0.18966,"object_to_goal_dist_start":0.21434,"object_z_max":0.20151,"peak_contact_force":0.08313,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22410.0,"raw_peak_contact_force":0.56973,"tcp_end":[0.49695,0.03545,0.21919],"tcp_start":[0.50005,0.03569,0.03877],"tcp_to_object_dist_end":0.02078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.62802,0.16958,0.19039],"object_pos_start":[0.50826,0.03645,0.20179],"object_to_goal_dist_end":0.04546,"object_to_goal_dist_start":0.18966,"object_z_max":0.25961,"peak_contact_force":0.07558,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25161.0,"raw_peak_contact_force":0.17133,"subtask_id":"transport_arc","tcp_end":[0.61923,0.16611,0.21185],"tcp_start":[0.49695,0.03545,0.21919],"tcp_to_object_dist_end":0.02346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61392,0.16359,0.02361],"object_pos_start":[0.62802,0.16958,0.19039],"object_to_goal_dist_end":0.1225,"object_to_goal_dist_start":0.04546,"object_z_max":0.19039,"peak_contact_force":0.14109,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2662.0,"raw_peak_contact_force":1.56265,"subtask_id":"release_1","tcp_end":[0.61378,0.16463,0.23084],"tcp_start":[0.61923,0.16611,0.21185],"tcp_to_object_dist_end":0.20723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.60963,0.16291,0.02721],"object_pos_start":[0.61392,0.16359,0.02361],"object_to_goal_dist_end":0.11956,"object_to_goal_dist_start":0.1225,"object_z_max":0.02722,"peak_contact_force":0.14795,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":40.0,"raw_peak_contact_force":0.14795,"tcp_end":[0.61525,0.16559,0.23118],"tcp_start":[0.61378,0.16463,0.23084],"tcp_to_object_dist_end":0.20406,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```