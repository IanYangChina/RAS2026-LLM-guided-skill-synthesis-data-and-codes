## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3481 | 0.42 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2235 | 0.42 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3719 | 0.42 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

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

## Current Skill (Q=0.348) — your mutation base

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

- **Composite score**: 0.348
- **task_score** (E): 0.416
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2540 |
| descend | 1.00 | 1.00 | 0.0043 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1333 |
| transport | 1.00 | 1.00 | 0.2002 |
| place | 1.00 | 1.00 | 0.0165 |
| release | 1.00 | 1.00 | 0.0213 |
| retract | 1.00 | 1.00 | 0.0241 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.049) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.049)→(0.508, 0.017, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.503, 0.016, 0.039)→(0.503, 0.016, 0.039) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.667 | 0.180 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.503, 0.016, 0.039)→(0.499, 0.016, 0.172) | (0.516, 0.017, 0.025)→(0.511, 0.017, 0.156) | 0.237→0.206 | 1.00 / 38.667 | 0.080 | 0.559 |
| transport | approach | 1.00 / step_budget | (0.499, 0.016, 0.172)→(0.595, 0.168, 0.225) | (0.511, 0.017, 0.156)→(0.599, 0.170, 0.203) | 0.206→0.038 | 1.00 / 43.667 | 0.071 | 0.278 |
| place | descend | 1.00 / force_exceeded | (0.595, 0.168, 0.225)→(0.597, 0.171, 0.209) | (0.599, 0.170, 0.203)→(0.600, 0.173, 0.186) | 0.038→0.030 | 1.00 / 40.333 | 3326.414 | 0.314 |
| release | release | 1.00 / step_budget | (0.597, 0.171, 0.209)→(0.592, 0.169, 0.229) | (0.600, 0.173, 0.186)→(0.588, 0.168, 0.020) | 0.030→0.149 | 1.00 / 3.333 | 4.426 | 1.586 |
| retract | retract | 1.00 / step_budget | (0.592, 0.169, 0.229)→(0.598, 0.175, 0.251) | (0.588, 0.168, 0.020)→(0.589, 0.169, 0.027) | 0.149→0.142 | 1.00 / 3.333 | 0.170 | 0.225 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.570
- phase_score: 0.427
- phase_breakdown.approach_1_score: 0.671
- phase_breakdown.descend_1_score: 0.809
- phase_breakdown.transport_arc_score: 0.251
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.168
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.570
- **Median Q (composite search score)**: 0.363
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.251


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71533,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.19713,"descend.descend_force_threshold":6.05952,"lift.lift_height":0.19305,"place.place_force_threshold":3.96426,"place.place_speed":0.11782,"retract.retract_speed":0.18686,"transport.arc_height":0.10766,"transport.transport_speed":0.09411},"optimized_scores":{"best_composite_score":0.42442,"best_fitness_score":0.75442,"best_task_score":0.57045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":249.0,"contact_point_centroid":[0.58188,0.17117,-0.00591],"force_p95":0.93267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37619,"mean_force":0.28225,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5902,0.1727,0.18695]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.5276,0.02731,-0.00158],"force_p95":0.49075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56906,"mean_force":0.11026,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51512,0.02747,0.04047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9562.0,"contact_point_centroid":[0.51331,0.04654,0.12781],"force_p95":0.08621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36827,"mean_force":0.0617,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51272,0.02733,0.12507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11796.0,"contact_point_centroid":[0.51427,0.00839,0.12428],"force_p95":0.08115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30828,"mean_force":0.05159,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51273,0.02733,0.1225]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5307,0.0306,-0.00232],"force_p95":0.19598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26022,"mean_force":0.14524,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51696,0.0276,0.03934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21.0,"contact_point_centroid":[0.59075,0.19266,0.18016],"force_p95":0.23884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24591,"mean_force":0.15129,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.59636,0.17448,0.17696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.60029,0.15554,0.17754],"force_p95":0.21586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23201,"mean_force":0.12896,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.59636,0.17448,0.17696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11850.0,"contact_point_centroid":[0.55788,0.083,0.23629],"force_p95":0.08237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20109,"mean_force":0.05005,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55454,0.10171,0.23486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1051.0,"contact_point_centroid":[0.58998,0.19259,0.174],"force_p95":0.08466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18823,"mean_force":0.04953,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59389,0.17388,0.1715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1233.0,"contact_point_centroid":[0.59864,0.15529,0.17108],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18034,"mean_force":0.04361,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5939,0.17389,0.1715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10337.0,"contact_point_centroid":[0.55273,0.12133,0.23713],"force_p95":0.09922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17492,"mean_force":0.05863,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55498,0.10247,0.23405]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6335.0,"contact_point_centroid":[0.5175,0.00861,0.04074],"force_p95":0.06908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15417,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51646,0.02757,0.03877]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51084,0.01359,0.17514]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.58184,0.17111,-0.00179],"force_p95":0.12922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13364,"mean_force":0.10412,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59046,0.17291,0.19653]},{"body_a":"world","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52246,0.02783,0.04646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4946.0,"contact_point_centroid":[0.51734,0.04701,0.04164],"force_p95":0.09234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09525,"mean_force":0.05462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51647,0.02757,0.03878]}],"total_contact_groups":16},"final_pose_error":0.01657,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5818,0.17106,0.02658],"final_tcp_position":[0.59106,0.17332,0.19637],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52345,0.02775,0.04845],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":48.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52172,0.02788,0.04477],"tcp_start":[0.52345,0.02775,0.04845],"tcp_to_object_dist_end":0.0209,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53059,0.02884,0.02506],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18533,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18653,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13085.0,"raw_peak_contact_force":0.26022,"subtask_id":"grasp_1","tcp_end":[0.51644,0.02757,0.03874],"tcp_start":[0.51644,0.02757,0.03874],"tcp_to_object_dist_end":0.01973,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.52541,0.02822,0.19443],"object_pos_start":[0.53061,0.02881,0.02511],"object_to_goal_dist_end":0.18936,"object_to_goal_dist_start":0.18533,"object_z_max":0.19416,"peak_contact_force":0.08238,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21444.0,"raw_peak_contact_force":0.56906,"tcp_end":[0.51324,0.02737,0.21217],"tcp_start":[0.51644,0.02757,0.03874],"tcp_to_object_dist_end":0.02153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.59611,0.17582,0.15374],"object_pos_start":[0.52541,0.02822,0.19443],"object_to_goal_dist_end":0.04605,"object_to_goal_dist_start":0.18936,"object_z_max":0.23582,"peak_contact_force":0.07419,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22187.0,"raw_peak_contact_force":0.20109,"subtask_id":"transport_arc","tcp_end":[0.59636,0.17448,0.17696],"tcp_start":[0.51324,0.02737,0.21217],"tcp_to_object_dist_end":0.02327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.59591,0.17582,0.15314],"object_pos_start":[0.59611,0.17582,0.15374],"object_to_goal_dist_end":0.04549,"object_to_goal_dist_start":0.04605,"object_z_max":0.15374,"peak_contact_force":9760.30694,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":43.0,"raw_peak_contact_force":0.24591,"subtask_id":"release_1","tcp_end":[0.59624,0.17449,0.17641],"tcp_start":[0.59636,0.17448,0.17696],"tcp_to_object_dist_end":0.0233,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58307,0.17106,0.0259],"object_pos_start":[0.59591,0.17582,0.15314],"object_to_goal_dist_end":0.08457,"object_to_goal_dist_start":0.04549,"object_z_max":0.15314,"peak_contact_force":0.0959,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2533.0,"raw_peak_contact_force":1.37619,"subtask_id":"release_1","tcp_end":[0.59013,0.17268,0.19632],"tcp_start":[0.59624,0.17449,0.17641],"tcp_to_object_dist_end":0.17057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.5818,0.17106,0.02658],"object_pos_start":[0.58307,0.17106,0.0259],"object_to_goal_dist_end":0.0842,"object_to_goal_dist_start":0.08457,"object_z_max":0.0266,"peak_contact_force":0.13364,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":0.13364,"tcp_end":[0.59106,0.17332,0.19637],"tcp_start":[0.59013,0.17268,0.19632],"tcp_to_object_dist_end":0.17005,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91262,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.27711,"descend.descend_force_threshold":9.99383,"lift.lift_height":0.13309,"place.place_force_threshold":3.36737,"place.place_speed":0.06293,"retract.retract_speed":0.26252,"transport.arc_height":0.07966,"transport.transport_speed":0.25109},"optimized_scores":{"best_composite_score":0.25663,"best_fitness_score":0.58663,"best_task_score":0.23114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.56295,0.16733,-0.0106],"force_p95":1.71901,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95527,"mean_force":0.66322,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5731,0.16991,0.31279]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50044,-0.0143,-0.00141],"force_p95":0.46592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53953,"mean_force":0.12328,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49083,-0.01432,0.04128]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.5771,0.1714,-0.00524],"force_p95":0.27897,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4027,"mean_force":0.1781,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57639,0.17472,0.32333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.57087,0.18876,0.30031],"force_p95":0.26794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37176,"mean_force":0.11291,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.57676,0.1706,0.29683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13623.0,"contact_point_centroid":[0.52223,0.03484,0.26176],"force_p95":0.09945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35392,"mean_force":0.05833,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5195,0.05367,0.25977]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6773.0,"contact_point_centroid":[0.48743,-0.0335,0.09965],"force_p95":0.07774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3163,"mean_force":0.05669,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48832,-0.0143,0.09721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7851.0,"contact_point_centroid":[0.48872,0.00476,0.09655],"force_p95":0.07423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30884,"mean_force":0.05021,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48833,-0.0143,0.09491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13521.0,"contact_point_centroid":[0.51844,0.07115,0.26095],"force_p95":0.093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26045,"mean_force":0.05609,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51882,0.0523,0.25869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.58052,0.15157,0.29822],"force_p95":0.1617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22878,"mean_force":0.0669,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.57676,0.1706,0.29683]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50387,-0.01565,-0.00213],"force_p95":0.1545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21173,"mean_force":0.13233,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49254,-0.01433,0.04038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1162.0,"contact_point_centroid":[0.57007,0.18925,0.29572],"force_p95":0.07551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15731,"mean_force":0.04563,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57537,0.1708,0.29276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1445.0,"contact_point_centroid":[0.57894,0.15176,0.29425],"force_p95":0.06376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14605,"mean_force":0.0375,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57538,0.17081,0.2928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6387.0,"contact_point_centroid":[0.49236,0.00476,0.04139],"force_p95":0.06541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14022,"mean_force":0.04128,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49205,-0.01432,0.03985]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49895,-0.00693,0.1759]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49797,-0.01429,0.04706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5377.0,"contact_point_centroid":[0.49133,-0.03361,0.04247],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07975,"mean_force":0.04937,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49205,-0.01432,0.03985]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57907,0.17108,0.02916],"final_tcp_position":[0.58026,0.18032,0.33067],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":191.99993,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49906,-0.01421,0.04911],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49719,-0.01435,0.04537],"tcp_start":[0.49906,-0.01421,0.04911],"tcp_to_object_dist_end":0.02049,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50377,-0.01498,0.0256],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1515,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13568.0,"raw_peak_contact_force":0.21173,"subtask_id":"grasp_1","tcp_end":[0.49203,-0.01432,0.03983],"tcp_start":[0.49203,-0.01432,0.03983],"tcp_to_object_dist_end":0.01846,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":363.0,"n_steps_budget":840.0,"object_pos_end":[0.49933,-0.0147,0.13721],"object_pos_start":[0.50377,-0.01498,0.02562],"object_to_goal_dist_end":0.24664,"object_to_goal_dist_start":0.31208,"object_z_max":0.13694,"peak_contact_force":0.07164,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14701.0,"raw_peak_contact_force":0.53953,"tcp_end":[0.48836,-0.01429,0.15349],"tcp_start":[0.49203,-0.01432,0.03983],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.58283,0.17279,0.27414],"object_pos_start":[0.49933,-0.0147,0.13721],"object_to_goal_dist_end":0.03014,"object_to_goal_dist_start":0.24664,"object_z_max":0.28709,"peak_contact_force":0.07127,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27144.0,"raw_peak_contact_force":0.35392,"subtask_id":"transport_arc","tcp_end":[0.57681,0.17033,0.29711],"tcp_start":[0.48836,-0.01429,0.15349],"tcp_to_object_dist_end":0.02388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.58235,0.17329,0.27312],"object_pos_start":[0.58283,0.17279,0.27414],"object_to_goal_dist_end":0.02909,"object_to_goal_dist_start":0.03014,"object_z_max":0.27414,"peak_contact_force":191.99993,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":180.0,"raw_peak_contact_force":0.37176,"subtask_id":"release_1","tcp_end":[0.57666,0.17094,0.29632],"tcp_start":[0.57681,0.17033,0.29711],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5759,0.1689,0.00755],"object_pos_start":[0.58235,0.17329,0.27312],"object_to_goal_dist_end":0.24153,"object_to_goal_dist_start":0.02909,"object_z_max":0.27312,"peak_contact_force":13.06385,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2728.0,"raw_peak_contact_force":1.95527,"subtask_id":"release_1","tcp_end":[0.57307,0.16991,0.31756],"tcp_start":[0.57666,0.17094,0.29632],"tcp_to_object_dist_end":0.31003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":78.0,"n_steps_budget":600.0,"object_pos_end":[0.57907,0.17108,0.02916],"object_pos_start":[0.5759,0.1689,0.00755],"object_to_goal_dist_end":0.21971,"object_to_goal_dist_start":0.24153,"object_z_max":0.03083,"peak_contact_force":0.2545,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":156.0,"raw_peak_contact_force":0.4027,"tcp_end":[0.58026,0.18032,0.33067],"tcp_start":[0.57307,0.16991,0.31756],"tcp_to_object_dist_end":0.30166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14615,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.16751,"descend.descend_force_threshold":5.74165,"lift.lift_height":0.13211,"place.place_force_threshold":5.69559,"place.place_speed":0.08529,"retract.retract_speed":0.17073,"transport.arc_height":0.06229,"transport.transport_speed":0.16719},"optimized_scores":{"best_composite_score":0.36313,"best_fitness_score":0.69313,"best_task_score":0.44571},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":282.0,"contact_point_centroid":[0.60587,0.16515,-0.00495],"force_p95":0.81538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42766,"mean_force":0.24769,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61298,0.1658,0.16371]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50953,0.03582,-0.00166],"force_p95":0.47028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56699,"mean_force":0.11748,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49872,0.03555,0.04072]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6097.0,"contact_point_centroid":[0.49628,0.05459,0.09676],"force_p95":0.09012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36406,"mean_force":0.06281,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49631,0.03537,0.09429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12033.0,"contact_point_centroid":[0.61047,0.18256,0.1734],"force_p95":0.06693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32301,"mean_force":0.04668,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.61551,0.16423,0.16991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7765.0,"contact_point_centroid":[0.49751,0.01642,0.09505],"force_p95":0.08246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29814,"mean_force":0.05066,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49631,0.03537,0.09358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11129.0,"contact_point_centroid":[0.54601,0.06771,0.20735],"force_p95":0.08605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27987,"mean_force":0.05352,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54317,0.08661,0.20574]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51277,0.03946,-0.00241],"force_p95":0.21402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27518,"mean_force":0.15104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50055,0.0357,0.03945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12606.0,"contact_point_centroid":[0.61925,0.14527,0.17084],"force_p95":0.06808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25038,"mean_force":0.04552,"phase_index":5.0,"phase_name":"place","phase_type":"descend","tcp_position_centroid":[0.61551,0.16423,0.16991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10117.0,"contact_point_centroid":[0.54503,0.10973,0.21039],"force_p95":0.08461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23967,"mean_force":0.05712,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54723,0.09085,0.20731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6311.0,"contact_point_centroid":[0.50102,0.01669,0.04031],"force_p95":0.07269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18008,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50005,0.03566,0.0389]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.60577,0.16517,-0.00196],"force_p95":0.13392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13994,"mean_force":0.12213,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61692,0.16806,0.19957]},{"body_a":"world","body_b":"grasp_target","contact_count":1812.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5028,0.01754,0.17529]},{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50597,0.03595,0.04643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.62083,0.14817,0.15089],"force_p95":0.0655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10294,"mean_force":0.03896,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61725,0.16705,0.15043]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4965.0,"contact_point_centroid":[0.50022,0.05516,0.04119],"force_p95":0.09506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0992,"mean_force":0.05506,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50007,0.03567,0.03892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1051.0,"contact_point_centroid":[0.61367,0.18585,0.15312],"force_p95":0.07823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0929,"mean_force":0.04792,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61722,0.16704,0.15038]}],"total_contact_groups":16},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60575,0.16517,0.02602],"final_tcp_position":[0.62229,0.1706,0.226],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1812.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50719,0.03582,0.04874],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":60.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.50521,0.03604,0.04458],"tcp_start":[0.50719,0.03582,0.04874],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51269,0.03721,0.02481],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21438,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20222,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13080.0,"raw_peak_contact_force":0.27518,"subtask_id":"grasp_1","tcp_end":[0.50003,0.03566,0.03888],"tcp_start":[0.50003,0.03566,0.03888],"tcp_to_object_dist_end":0.01899,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":363.0,"n_steps_budget":840.0,"object_pos_end":[0.50807,0.03653,0.13519],"object_pos_start":[0.51271,0.03717,0.02487],"object_to_goal_dist_end":0.1813,"object_to_goal_dist_start":0.21436,"object_z_max":0.13492,"peak_contact_force":0.08535,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13949.0,"raw_peak_contact_force":0.56699,"tcp_end":[0.49633,0.03537,0.15151],"tcp_start":[0.50003,0.03566,0.03888],"tcp_to_object_dist_end":0.02014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.6189,0.16237,0.18037],"object_pos_start":[0.50807,0.03653,0.13519],"object_to_goal_dist_end":0.03778,"object_to_goal_dist_start":0.1813,"object_z_max":0.20953,"peak_contact_force":0.06824,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21246.0,"raw_peak_contact_force":0.27987,"subtask_id":"transport_arc","tcp_end":[0.61325,0.15991,0.20095],"tcp_start":[0.49633,0.03537,0.15151],"tcp_to_object_dist_end":0.02149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.62116,0.16952,0.13099],"object_pos_start":[0.6189,0.16237,0.18037],"object_to_goal_dist_end":0.01572,"object_to_goal_dist_start":0.03778,"object_z_max":0.18037,"peak_contact_force":26.93473,"phase_name":"place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24639.0,"raw_peak_contact_force":0.32301,"subtask_id":"release_1","tcp_end":[0.61897,0.16749,0.15386],"tcp_start":[0.61325,0.15991,0.20095],"tcp_to_object_dist_end":0.02307,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60641,0.16517,0.02642],"object_pos_start":[0.62116,0.16952,0.13099],"object_to_goal_dist_end":0.12071,"object_to_goal_dist_start":0.01572,"object_z_max":0.13099,"peak_contact_force":0.11931,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2661.0,"raw_peak_contact_force":1.42766,"subtask_id":"release_1","tcp_end":[0.61289,0.16578,0.17419],"tcp_start":[0.61897,0.16749,0.15386],"tcp_to_object_dist_end":0.14792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":600.0,"object_pos_end":[0.60575,0.16517,0.02602],"object_pos_start":[0.60641,0.16517,0.02642],"object_to_goal_dist_end":0.12121,"object_to_goal_dist_start":0.12071,"object_z_max":0.02654,"peak_contact_force":0.12275,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":880.0,"raw_peak_contact_force":0.13994,"tcp_end":[0.62229,0.1706,0.226],"tcp_start":[0.61289,0.16578,0.17419],"tcp_to_object_dist_end":0.20074,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```