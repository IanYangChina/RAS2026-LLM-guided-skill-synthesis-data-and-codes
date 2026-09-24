## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1958 | 0.51 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4108 | 0.82 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.5034 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4745 | 0.95 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1790 | 0.41 | ✅ accepted |

**Proposal policy**: task_score is 0.51 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.196) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
    orientation:
      mode: none
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: none
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
    orientation:
      mode: none
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
    - 0.2
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_1
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
    - 0.15
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_goal
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
    - 0.03
    orientation:
      mode: none
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: placement_force
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=placement_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0

## Design Metrics

- **Composite score**: 0.196
- **task_score** (E): 0.508
- **fitness_score**: 0.716  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0378 |
| descend_1 | 1.00 | 1.00 | 0.2288 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.67 | 1.00 | 0.1150 |
| transport_1 | 0.67 | 1.00 | 0.1994 |
| descend_goal | 1.00 | 1.00 | 0.0936 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.018, 0.285) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.125 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.018, 0.285)→(0.511, 0.018, 0.056) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 11.677 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.056)→(0.502, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 44.667 | 0.147 | 0.192 |
| lift_1 | lift | 0.67 / step_budget | (0.502, 0.018, 0.046)→(0.498, 0.017, 0.161) | (0.516, 0.018, 0.026)→(0.506, 0.018, 0.133) | 0.236→0.200 | 1.00 / 30.000 | 106.107 | 0.425 |
| transport_1 | approach | 0.67 / step_budget | (0.498, 0.017, 0.161)→(0.579, 0.138, 0.288) | (0.506, 0.018, 0.133)→(0.564, 0.097, 0.080) | 0.200→0.182 | 1.00 / 14.000 | 0.104 | 1.382 |
| descend_goal | descend | 1.00 / step_budget | (0.579, 0.138, 0.288)→(0.599, 0.174, 0.209) | (0.564, 0.097, 0.080)→(0.564, 0.103, 0.048) | 0.182→0.153 | 1.00 / 9.333 | 3249.702 | 0.228 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.246
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.274
- phase_breakdown.transport_arc_score: 0.066
- phase_breakdown.descend_1_score: 0.866
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.014
- grasp_place_fitness: 0.964

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.964
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.139
- **K-run variance**: 0.0336
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75714,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20682,"descend_1.depth":0.02052,"descend_goal.place_z_offset":0.03322,"lift_1.lift_height":0.15335,"lift_1.speed":0.0587,"transport_1.arc_height":0.28292,"transport_1.speed":0.39101,"transport_1.transport_height":0.13956},"optimized_scores":{"best_composite_score":0.44351,"best_fitness_score":0.96351,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2940.0,"contact_point_centroid":[0.58279,0.18221,0.19334],"force_p95":0.13722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43505,"mean_force":0.0939,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58928,0.16443,0.19569]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.52543,0.02908,-0.00121],"force_p95":0.25065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4116,"mean_force":0.08866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51469,0.02953,0.04657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3456.0,"contact_point_centroid":[0.59128,0.1458,0.19291],"force_p95":0.13217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33453,"mean_force":0.08307,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58904,0.16402,0.19787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16362.0,"contact_point_centroid":[0.53728,0.09698,0.20008],"force_p95":0.09781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33153,"mean_force":0.06002,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5386,0.07812,0.19973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17730.0,"contact_point_centroid":[0.54295,0.06239,0.20111],"force_p95":0.09538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32704,"mean_force":0.05775,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54035,0.08101,0.20209]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19471.0,"contact_point_centroid":[0.51254,0.04854,0.09313],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27364,"mean_force":0.05174,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51232,0.02938,0.09066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20571.0,"contact_point_centroid":[0.51357,0.01029,0.09089],"force_p95":0.07737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25384,"mean_force":0.04957,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5123,0.02938,0.08951]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03083,-0.0021],"force_p95":0.14963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19899,"mean_force":0.13002,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51795,0.02975,0.04633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5544.0,"contact_point_centroid":[0.51772,0.01053,0.04694],"force_p95":0.06625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1416,"mean_force":0.03968,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51672,0.02967,0.0449]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5124,0.01465,0.27419]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52355,0.02872,0.14849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4688.0,"contact_point_centroid":[0.51694,0.04898,0.04805],"force_p95":0.07633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07791,"mean_force":0.0468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51672,0.02967,0.04491]}],"total_contact_groups":12},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58741,0.17455,0.11152],"final_tcp_position":[0.59535,0.1743,0.1476],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":34.78496,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52427,0.02737,0.24378],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":34.78496,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52528,0.03023,0.05494],"tcp_start":[0.52427,0.02737,0.24378],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.03034,0.02564],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18391,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14861,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12032.0,"raw_peak_contact_force":0.19899,"subtask_id":"grasp_1","tcp_end":[0.51669,0.02966,0.04487],"tcp_start":[0.52528,0.03023,0.05494],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51837,0.03,0.11387],"object_pos_start":[0.53047,0.03034,0.02564],"object_to_goal_dist_end":0.17037,"object_to_goal_dist_start":0.18391,"object_z_max":0.11377,"peak_contact_force":0.07971,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40254.0,"raw_peak_contact_force":0.4116,"tcp_end":[0.51248,0.02939,0.13956],"tcp_start":[0.51669,0.02966,0.04487],"tcp_to_object_dist_end":0.02636,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58622,0.15822,0.20832],"object_pos_start":[0.51837,0.03,0.11387],"object_to_goal_dist_end":0.10342,"object_to_goal_dist_start":0.17037,"object_z_max":0.20847,"peak_contact_force":0.10084,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34092.0,"raw_peak_contact_force":0.33153,"subtask_id":"transport_arc","tcp_end":[0.58591,0.15633,0.24117],"tcp_start":[0.51248,0.02939,0.13956],"tcp_to_object_dist_end":0.03291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.58741,0.17455,0.11152],"object_pos_start":[0.58622,0.15822,0.20832],"object_to_goal_dist_end":0.01508,"object_to_goal_dist_start":0.10342,"object_z_max":0.20832,"peak_contact_force":0.15006,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6396.0,"raw_peak_contact_force":0.43505,"tcp_end":[0.59535,0.1743,0.1476],"tcp_start":[0.58591,0.15633,0.24117],"tcp_to_object_dist_end":0.03694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85926,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26697,"descend_1.depth":0.02421,"descend_goal.place_z_offset":0.04714,"lift_1.lift_height":0.13693,"lift_1.speed":0.24134,"transport_1.arc_height":0.05309,"transport_1.speed":0.2944,"transport_1.transport_height":0.16843},"optimized_scores":{"best_composite_score":0.00518,"best_fitness_score":0.52518,"best_task_score":0.1329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2731.0,"contact_point_centroid":[0.5108,0.00864,-0.00239],"force_p95":0.125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8105,"mean_force":0.13946,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51567,0.04741,0.31233]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.50095,-0.01478,-0.00114],"force_p95":0.24401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40107,"mean_force":0.06642,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48913,-0.01506,0.05128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7414.0,"contact_point_centroid":[0.48916,0.00359,0.09514],"force_p95":0.13121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29619,"mean_force":0.07476,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48675,-0.01504,0.09657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7263.0,"contact_point_centroid":[0.4888,-0.03385,0.09575],"force_p95":0.12879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29525,"mean_force":0.07625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48675,-0.01504,0.09667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1955.0,"contact_point_centroid":[0.49173,0.0077,0.18951],"force_p95":0.13347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29173,"mean_force":0.10306,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4866,-0.01021,0.1938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1807.0,"contact_point_centroid":[0.49099,-0.02894,0.18762],"force_p95":0.15704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29061,"mean_force":0.11135,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4864,-0.01072,0.1916]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01567,-0.00205],"force_p95":0.1379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17268,"mean_force":0.12661,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49186,-0.01508,0.05081]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.50382,-0.01567,-0.00128],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49969,-0.00265,0.2987]},{"body_a":"world","body_b":"grasp_target","contact_count":2900.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12867,"mean_force":0.12268,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49847,-0.01085,0.17658]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51082,0.00862,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56189,0.14156,0.33051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.49144,0.00405,0.04972],"force_p95":0.07088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10741,"mean_force":0.04717,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49067,-0.01507,0.0495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4654.0,"contact_point_centroid":[0.49119,-0.03427,0.05049],"force_p95":0.07346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08235,"mean_force":0.0467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49067,-0.01507,0.0495]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2727.0,"contact_point_centroid":[0.51737,0.05062,0.31977],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01513,"mean_force":0.01044,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51732,0.05064,0.31741]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1930.0,"contact_point_centroid":[0.56161,0.14138,0.33279],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56186,0.14151,0.33056]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51082,0.00862,0.01602],"final_tcp_position":[0.5809,0.17956,0.29422],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.83449,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":47.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02591],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31231,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12911,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":184.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50001,-0.00662,0.29635],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02591],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31231,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2900.0,"raw_peak_contact_force":0.12867,"subtask_id":"descend_1","tcp_end":[0.49898,-0.01512,0.05868],"tcp_start":[0.50001,-0.00662,0.29635],"tcp_to_object_dist_end":0.03303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50375,-0.01538,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31222,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13751,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11054.0,"raw_peak_contact_force":0.17268,"subtask_id":"grasp_1","tcp_end":[0.49064,-0.01507,0.04947],"tcp_start":[0.49898,-0.01512,0.05868],"tcp_to_object_dist_end":0.02706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49435,-0.01528,0.13791],"object_pos_start":[0.50375,-0.01538,0.0258],"object_to_goal_dist_end":0.24862,"object_to_goal_dist_start":0.31222,"object_z_max":0.13774,"peak_contact_force":0.12602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14813.0,"raw_peak_contact_force":0.40107,"tcp_end":[0.48699,-0.01503,0.17166],"tcp_start":[0.49064,-0.01507,0.04947],"tcp_to_object_dist_end":0.03454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51082,0.00862,0.01602],"object_pos_start":[0.49435,-0.01528,0.13791],"object_to_goal_dist_end":0.30272,"object_to_goal_dist_start":0.24862,"object_z_max":0.18052,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9220.0,"raw_peak_contact_force":1.8105,"subtask_id":"transport_arc","tcp_end":[0.54403,0.10356,0.37191],"tcp_start":[0.48699,-0.01503,0.17166],"tcp_to_object_dist_end":0.36983,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.51082,0.00862,0.01602],"object_pos_start":[0.51082,0.00862,0.01602],"object_to_goal_dist_end":0.30272,"object_to_goal_dist_start":0.30272,"object_z_max":0.01602,"peak_contact_force":9748.83449,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3730.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5809,0.17956,0.29422],"tcp_start":[0.54403,0.10356,0.37191],"tcp_to_object_dist_end":0.33396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88571,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29109,"descend_1.depth":0.02001,"descend_goal.place_z_offset":0.03362,"lift_1.lift_height":0.14109,"lift_1.speed":0.11392,"transport_1.arc_height":0.28664,"transport_1.speed":0.24186,"transport_1.transport_height":0.1098},"optimized_scores":{"best_composite_score":0.13875,"best_fitness_score":0.65875,"best_task_score":0.3903},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":251.0,"contact_point_centroid":[0.59437,0.12551,-0.00732],"force_p95":1.15995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00299,"mean_force":0.32912,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60344,0.15006,0.25236]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10382.0,"contact_point_centroid":[0.53381,0.05772,0.21481],"force_p95":0.12523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50804,"mean_force":0.08341,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52966,0.07541,0.21769]},{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.50924,0.03772,-0.00134],"force_p95":0.23618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46135,"mean_force":0.08003,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49745,0.03821,0.04665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8847.0,"contact_point_centroid":[0.53179,0.09576,0.21727],"force_p95":0.14386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35541,"mean_force":0.09114,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53133,0.07713,0.22006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13943.0,"contact_point_centroid":[0.49541,0.05721,0.10781],"force_p95":0.08436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29173,"mean_force":0.05425,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49517,0.03803,0.10572]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14431.0,"contact_point_centroid":[0.49697,0.01902,0.10476],"force_p95":0.08405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29035,"mean_force":0.05201,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49514,0.03803,0.10384]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03975,-0.00212],"force_p95":0.15549,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20558,"mean_force":0.13124,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50039,0.03846,0.0464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.50094,0.01917,0.04641],"force_p95":0.07258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1557,"mean_force":0.04446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49918,0.03836,0.04506]},{"body_a":"world","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50302,0.01659,0.30791]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.59475,0.12565,-0.00194],"force_p95":0.12537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12649,"mean_force":0.12071,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61319,0.16097,0.21741]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50699,0.03641,0.18333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5178.0,"contact_point_centroid":[0.4985,0.05756,0.0489],"force_p95":0.07221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07492,"mean_force":0.04259,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49918,0.03836,0.04506]},{"body_a":"left_finger","body_b":"right_finger","contact_count":106.0,"contact_point_centroid":[0.60507,0.15204,0.25459],"force_p95":0.01527,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01567,"mean_force":0.01268,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60566,0.1523,0.25207]},{"body_a":"left_finger","body_b":"right_finger","contact_count":917.0,"contact_point_centroid":[0.61307,0.16081,0.21964],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6132,0.16098,0.21737]}],"total_contact_groups":14},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59475,0.12566,0.01602],"final_tcp_position":[0.62045,0.16827,0.18386],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":318.11615,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1340.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5083,0.03392,0.31421],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5076,0.03904,0.05454],"tcp_start":[0.5083,0.03392,0.31421],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51252,0.0391,0.02558],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21285,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15447,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11954.0,"raw_peak_contact_force":0.20558,"subtask_id":"grasp_1","tcp_end":[0.49915,0.03835,0.04502],"tcp_start":[0.5076,0.03904,0.05454],"tcp_to_object_dist_end":0.02361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":713.0,"n_steps_budget":780.0,"object_pos_end":[0.50463,0.03903,0.14574],"object_pos_start":[0.51252,0.0391,0.02558],"object_to_goal_dist_end":0.18148,"object_to_goal_dist_start":0.21285,"object_z_max":0.14561,"peak_contact_force":318.11615,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28537.0,"raw_peak_contact_force":0.46135,"tcp_end":[0.49548,0.03806,0.17301],"tcp_start":[0.49915,0.03835,0.04502],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59502,0.12552,0.01601],"object_pos_start":[0.50463,0.03903,0.14574],"object_to_goal_dist_end":0.14112,"object_to_goal_dist_start":0.18148,"object_z_max":0.21601,"peak_contact_force":0.08853,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19586.0,"raw_peak_contact_force":2.00299,"subtask_id":"transport_arc","tcp_end":[0.6081,0.15461,0.25169],"tcp_start":[0.49548,0.03806,0.17301],"tcp_to_object_dist_end":0.23784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.59475,0.12566,0.01602],"object_pos_start":[0.59502,0.12552,0.01601],"object_to_goal_dist_end":0.14112,"object_to_goal_dist_start":0.14112,"object_z_max":0.01677,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1769.0,"raw_peak_contact_force":0.12649,"tcp_end":[0.62045,0.16827,0.18386],"tcp_start":[0.6081,0.15461,0.25169],"tcp_to_object_dist_end":0.17506,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```