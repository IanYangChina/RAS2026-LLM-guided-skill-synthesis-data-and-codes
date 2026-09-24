## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 7 | 0.1120 | 0.36 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0916 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0128 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3728 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3608 | 0.17 | ❌ rejected |

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
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.112) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_object
  target_entity: object
  weight: 0.6
phases:
- id: approach_object
  type: approach
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_grasp
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
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
- id: lift
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_lift_check
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport
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
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_lift_check
    when: before_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: descend_to_place
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
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_lift_check, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_lift_check, when=before_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.112
- **task_score** (E): 0.357
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1098 |
| descend_to_grasp | 1.00 | 1.00 | 0.1420 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 0.67 | 1.00 | 0.0942 |
| transport | 0.67 | 1.00 | 0.2589 |
| descend_to_place | 1.00 | 1.00 | 0.1086 |
| release | 1.00 | 1.00 | 0.0196 |
| retract | 1.00 | 1.00 | 0.0454 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.055)→(0.502, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 44.333 | 0.139 | 0.184 |
| lift | lift | 0.67 / step_budget | (0.502, -0.016, 0.045)→(0.509, -0.016, 0.139) | (0.515, -0.016, 0.026)→(0.519, -0.016, 0.114) | 0.270→0.236 | 1.00 / 31.000 | 0.086 | 0.398 |
| transport | approach | 0.67 / step_budget | (0.509, -0.016, 0.139)→(0.607, 0.161, 0.293) | (0.519, -0.016, 0.114)→(0.608, 0.151, 0.103) | 0.236→0.123 | 1.00 / 10.333 | 0.145 | 1.262 |
| descend_to_place | descend | 1.00 / step_budget | (0.607, 0.161, 0.293)→(0.613, 0.176, 0.186) | (0.608, 0.151, 0.103)→(0.616, 0.153, 0.015) | 0.123→0.160 | 1.00 / 8.333 | 94253.746 | 0.798 |
| release | release | 1.00 / step_budget | (0.613, 0.176, 0.186)→(0.607, 0.175, 0.205) | (0.616, 0.153, 0.015)→(0.616, 0.153, 0.016) | 0.160→0.159 | 1.00 / 4.000 | 0.123 | 0.124 |
| retract | retract | 1.00 / step_budget | (0.607, 0.175, 0.205)→(0.613, 0.180, 0.250) | (0.616, 0.153, 0.016)→(0.616, 0.153, 0.016) | 0.159→0.159 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.485
- phase_score: 0.574
- phase_breakdown.lift_object_score: 0.486
- phase_breakdown.reach_object_score: 0.225
- phase_breakdown.place_object_score: 0.676
- grasp_place_fitness: 0.706

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.706
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.485
- **Median Q (composite search score)**: 0.091
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.342


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42105,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.06309,"descend_to_grasp.descend_speed":0.10378,"descend_to_place.descend_speed":0.08157,"lift.lift_height":0.12416,"lift.lift_speed":0.1272,"retract.retract_speed":0.11171,"transport.speed":0.0324},"optimized_scores":{"best_composite_score":0.06907,"best_fitness_score":0.59907,"best_task_score":0.27102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":211.0,"contact_point_centroid":[0.62329,0.1884,-0.00897],"force_p95":1.27542,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14397,"mean_force":0.41229,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60257,0.21105,0.23633]},{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.5351,-0.02015,-0.00128],"force_p95":0.21953,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40569,"mean_force":0.06438,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52137,-0.02044,0.0461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.60159,0.20317,0.30209],"force_p95":0.23909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32978,"mean_force":0.17357,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59523,0.18522,0.3082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9161.0,"contact_point_centroid":[0.5275,-0.00152,0.0856],"force_p95":0.09101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27136,"mean_force":0.0606,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52451,-0.02048,0.08316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9152.0,"contact_point_centroid":[0.52742,-0.03949,0.08487],"force_p95":0.09379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26749,"mean_force":0.06109,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52448,-0.02048,0.08275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":291.0,"contact_point_centroid":[0.602,0.1698,0.30291],"force_p95":0.19593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23986,"mean_force":0.09141,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59545,0.18607,0.30534]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11581.0,"contact_point_centroid":[0.56624,0.09707,0.21858],"force_p95":0.12645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23422,"mean_force":0.08113,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56032,0.07835,0.21809]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02123,-0.00208],"force_p95":0.14369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1922,"mean_force":0.12853,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52392,-0.02049,0.04596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12839.0,"contact_point_centroid":[0.56755,0.06425,0.22243],"force_p95":0.09701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14622,"mean_force":0.07325,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56178,0.08277,0.22198]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51238,-0.0082,0.24956]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62408,0.18864,-0.00196],"force_p95":0.12532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12627,"mean_force":0.11715,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60051,0.21543,0.22169]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52838,-0.01891,0.12611]},{"body_a":"world","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.62408,0.18864,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60233,0.21975,0.26403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4847.0,"contact_point_centroid":[0.52376,-0.00124,0.04725],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10026,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52273,-0.02046,0.04459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5244.0,"contact_point_centroid":[0.52324,-0.03969,0.04697],"force_p95":0.0674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07354,"mean_force":0.04227,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52273,-0.02046,0.04459]},{"body_a":"left_finger","body_b":"right_finger","contact_count":56.0,"contact_point_centroid":[0.60449,0.21517,0.22825],"force_p95":0.01612,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01346,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60387,0.21515,0.22622]}],"total_contact_groups":17},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62408,0.18864,0.01602],"final_tcp_position":[0.60639,0.2247,0.28808],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273012.3338,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":892.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52715,-0.01727,0.19642],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53149,-0.02061,0.05515],"tcp_start":[0.52715,-0.01727,0.19642],"tcp_to_object_dist_end":0.02966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02071,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31644,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14178,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11891.0,"raw_peak_contact_force":0.1922,"tcp_end":[0.5227,-0.02046,0.04456],"tcp_start":[0.53149,-0.02061,0.05515],"tcp_to_object_dist_end":0.02363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":537.0,"n_steps_budget":600.0,"object_pos_end":[0.54566,-0.02062,0.11202],"object_pos_start":[0.53696,-0.02071,0.02571],"object_to_goal_dist_end":0.27381,"object_to_goal_dist_start":0.31644,"object_z_max":0.11189,"peak_contact_force":0.08666,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18495.0,"raw_peak_contact_force":0.40569,"subtask_id":"lift_object","tcp_end":[0.53183,-0.02061,0.1363],"tcp_start":[0.5227,-0.02046,0.04456],"tcp_to_object_dist_end":0.02794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59989,0.18386,0.27818],"object_pos_start":[0.54566,-0.02062,0.11202],"object_to_goal_dist_end":0.08392,"object_to_goal_dist_start":0.27381,"object_z_max":0.27804,"peak_contact_force":0.23422,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24420.0,"raw_peak_contact_force":0.23422,"tcp_end":[0.5948,0.18393,0.31073],"tcp_start":[0.53183,-0.02061,0.1363],"tcp_to_object_dist_end":0.03295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.62425,0.18911,0.01352],"object_pos_start":[0.59989,0.18386,0.27818],"object_to_goal_dist_end":0.19819,"object_to_goal_dist_start":0.08392,"object_z_max":0.27819,"peak_contact_force":273012.3338,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":639.0,"raw_peak_contact_force":2.14397,"subtask_id":"place_object","tcp_end":[0.60431,0.21661,0.22265],"tcp_start":[0.5948,0.18393,0.31073],"tcp_to_object_dist_end":0.21187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62408,0.18864,0.01602],"object_pos_start":[0.62425,0.18911,0.01352],"object_to_goal_dist_end":0.19583,"object_to_goal_dist_start":0.19819,"object_z_max":0.01683,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12627,"tcp_end":[0.59932,0.21485,0.24118],"tcp_start":[0.60431,0.21661,0.22265],"tcp_to_object_dist_end":0.22803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":600.0,"object_pos_end":[0.62408,0.18864,0.01602],"object_pos_start":[0.62408,0.18864,0.01602],"object_to_goal_dist_end":0.19583,"object_to_goal_dist_start":0.19583,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":828.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60639,0.2247,0.28808],"tcp_start":[0.59932,0.21485,0.24118],"tcp_to_object_dist_end":0.27501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44882,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.14942,"descend_to_grasp.descend_speed":0.0837,"descend_to_place.descend_speed":0.08802,"lift.lift_height":0.1249,"lift.lift_speed":0.12065,"retract.retract_speed":0.02574,"transport.speed":0.06406},"optimized_scores":{"best_composite_score":0.09124,"best_fitness_score":0.62124,"best_task_score":0.31537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":818.0,"contact_point_centroid":[0.63053,0.10097,-0.00364],"force_p95":0.74849,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74346,"mean_force":0.18551,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.61803,0.13814,0.29258]},{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.54363,-0.02794,-0.0013],"force_p95":0.21948,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41016,"mean_force":0.06554,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52933,-0.02796,0.04562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8488.0,"contact_point_centroid":[0.53636,-0.04696,0.08523],"force_p95":0.10013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27063,"mean_force":0.0656,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53281,-0.02804,0.08333]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8543.0,"contact_point_centroid":[0.5361,-0.00915,0.0853],"force_p95":0.10111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26819,"mean_force":0.06448,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53274,-0.02804,0.08279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7300.0,"contact_point_centroid":[0.572,0.04953,0.19004],"force_p95":0.14487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24814,"mean_force":0.08576,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56561,0.03084,0.18868]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02912,-0.00211],"force_p95":0.15144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21236,"mean_force":0.13081,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53195,-0.02804,0.04545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8508.0,"contact_point_centroid":[0.57384,0.01658,0.19322],"force_p95":0.1095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18832,"mean_force":0.07488,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56762,0.03502,0.19268]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51621,-0.01146,0.24859]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.6305,0.10114,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62756,0.15899,0.25512]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53598,-0.026,0.12567]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6305,0.10114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62443,0.16096,0.19466]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.6305,0.10114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62508,0.16173,0.23442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.53161,-0.00883,0.04711],"force_p95":0.06812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10856,"mean_force":0.04276,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53075,-0.02801,0.04404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.53184,-0.04731,0.0458],"force_p95":0.07215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07378,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53076,-0.02801,0.04404]},{"body_a":"left_finger","body_b":"right_finger","contact_count":713.0,"contact_point_centroid":[0.62015,0.14156,0.29814],"force_p95":0.01311,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.0108,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.61973,0.14156,0.2959]},{"body_a":"left_finger","body_b":"right_finger","contact_count":825.0,"contact_point_centroid":[0.62791,0.159,0.25717],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01058,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62756,0.159,0.25495]}],"total_contact_groups":17},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6305,0.10114,0.01602],"final_tcp_position":[0.62864,0.16336,0.25756],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.74346,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53452,-0.02387,0.19556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5396,-0.02825,0.0549],"tcp_start":[0.53452,-0.02387,0.19556],"tcp_to_object_dist_end":0.02951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.0284,0.0256],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26057,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1476,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11828.0,"raw_peak_contact_force":0.21236,"tcp_end":[0.53072,-0.02801,0.044],"tcp_start":[0.5396,-0.02825,0.0549],"tcp_to_object_dist_end":0.02363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":540.0,"n_steps_budget":600.0,"object_pos_end":[0.55421,-0.02822,0.11236],"object_pos_start":[0.54555,-0.0284,0.0256],"object_to_goal_dist_end":0.21831,"object_to_goal_dist_start":0.26057,"object_z_max":0.11223,"peak_contact_force":0.08642,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17227.0,"raw_peak_contact_force":0.41016,"subtask_id":"lift_object","tcp_end":[0.54035,-0.02824,0.13665],"tcp_start":[0.53072,-0.02801,0.044],"tcp_to_object_dist_end":0.02797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.6305,0.10114,0.01602],"object_pos_start":[0.55421,-0.02822,0.11236],"object_to_goal_dist_end":0.1731,"object_to_goal_dist_start":0.21831,"object_z_max":0.22417,"peak_contact_force":0.12262,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17339.0,"raw_peak_contact_force":1.74346,"tcp_end":[0.627,0.15617,0.31004],"tcp_start":[0.54035,-0.02824,0.13665],"tcp_to_object_dist_end":0.29915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.6305,0.10114,0.01602],"object_pos_start":[0.6305,0.10114,0.01602],"object_to_goal_dist_end":0.1731,"object_to_goal_dist_start":0.1731,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1609.0,"raw_peak_contact_force":0.12264,"subtask_id":"place_object","tcp_end":[0.62877,0.16219,0.19607],"tcp_start":[0.627,0.15617,0.31004],"tcp_to_object_dist_end":0.19013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6305,0.10114,0.01602],"object_pos_start":[0.6305,0.10114,0.01602],"object_to_goal_dist_end":0.1731,"object_to_goal_dist_start":0.1731,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62301,0.16049,0.21406],"tcp_start":[0.62877,0.16219,0.19607],"tcp_to_object_dist_end":0.20688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.6305,0.10114,0.01602],"object_pos_start":[0.6305,0.10114,0.01602],"object_to_goal_dist_end":0.1731,"object_to_goal_dist_start":0.1731,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":900.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62864,0.16336,0.25756],"tcp_start":[0.62301,0.16049,0.21406],"tcp_to_object_dist_end":0.24943,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46903,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.09964,"descend_to_grasp.descend_speed":0.06963,"descend_to_place.descend_speed":0.05297,"lift.lift_height":0.17013,"lift.lift_speed":0.05306,"retract.retract_speed":0.15131,"transport.speed":0.14752},"optimized_scores":{"best_composite_score":0.17554,"best_fitness_score":0.70554,"best_task_score":0.48529},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":205.0,"contact_point_centroid":[0.59468,0.16636,-0.00744],"force_p95":1.34286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80943,"mean_force":0.39577,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59445,0.13904,0.25376]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.46013,-0.00053,-0.00114],"force_p95":0.27407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3787,"mean_force":0.06227,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45071,-0.00021,0.04908]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6282.0,"contact_point_centroid":[0.50284,0.02844,0.17766],"force_p95":0.14057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32411,"mean_force":0.08318,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50079,0.04692,0.17944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17723.0,"contact_point_centroid":[0.45077,-0.01944,0.09772],"force_p95":0.08386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2783,"mean_force":0.05691,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45197,-0.00027,0.09683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20315.0,"contact_point_centroid":[0.45157,0.01872,0.09697],"force_p95":0.07428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26582,"mean_force":0.0505,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45192,-0.00027,0.09626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6180.0,"contact_point_centroid":[0.50744,0.06937,0.18052],"force_p95":0.12946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22369,"mean_force":0.08541,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50486,0.0509,0.18269]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00014,-0.00202],"force_p95":0.12935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14769,"mean_force":0.12452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45307,-0.00018,0.04851]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48435,-4e-05,0.25123]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.59444,0.16844,-0.00197],"force_p95":0.12521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12627,"mean_force":0.11866,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60125,0.14683,0.20127]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46302,-9e-05,0.12796]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59444,0.16844,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59928,0.14876,0.14024]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.59444,0.16844,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60034,0.14951,0.18105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.45132,-0.0194,0.04899],"force_p95":0.07593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09829,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45202,-0.00019,0.04749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45214,0.01887,0.04875],"force_p95":0.06782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08799,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45202,-0.00019,0.04749]},{"body_a":"left_finger","body_b":"right_finger","contact_count":16.0,"contact_point_centroid":[0.59943,0.14369,0.25954],"force_p95":0.01638,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01573,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59915,0.14369,0.25746]},{"body_a":"left_finger","body_b":"right_finger","contact_count":923.0,"contact_point_centroid":[0.60171,0.14685,0.20338],"force_p95":0.01216,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0148,"mean_force":0.01073,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60126,0.14683,0.20116]}],"total_contact_groups":17},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59444,0.16844,0.01602],"final_tcp_position":[0.60462,0.15111,0.20315],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.78169,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":788.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46785,-7e-05,0.19911],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45985,-0.00011,0.05545],"tcp_start":[0.46785,-7e-05,0.19911],"tcp_to_object_dist_end":0.02959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00033,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1288,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14769,"tcp_end":[0.45199,-0.00019,0.04746],"tcp_start":[0.45985,-0.00011,0.05545],"tcp_to_object_dist_end":0.0241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45738,-0.00014,0.11628],"object_pos_start":[0.46277,-0.00033,0.02591],"object_to_goal_dist_end":0.2163,"object_to_goal_dist_start":0.23337,"object_z_max":0.1162,"peak_contact_force":0.0856,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38202.0,"raw_peak_contact_force":0.3787,"subtask_id":"lift_object","tcp_end":[0.45554,-0.00031,0.14465],"tcp_start":[0.45199,-0.00019,0.04746],"tcp_to_object_dist_end":0.02843,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.59366,0.16825,0.014],"object_pos_start":[0.45738,-0.00014,0.11628],"object_to_goal_dist_end":0.11052,"object_to_goal_dist_start":0.2163,"object_z_max":0.19442,"peak_contact_force":0.0792,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12683.0,"raw_peak_contact_force":1.80943,"tcp_end":[0.59955,0.1441,0.25777],"tcp_start":[0.45554,-0.00031,0.14465],"tcp_to_object_dist_end":0.24504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.59444,0.16844,0.01602],"object_pos_start":[0.59366,0.16825,0.014],"object_to_goal_dist_end":0.10845,"object_to_goal_dist_start":0.11052,"object_z_max":0.01666,"peak_contact_force":9748.78169,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1795.0,"raw_peak_contact_force":0.12627,"subtask_id":"place_object","tcp_end":[0.60443,0.15012,0.14068],"tcp_start":[0.59955,0.1441,0.25777],"tcp_to_object_dist_end":0.12639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59444,0.16844,0.01602],"object_pos_start":[0.59444,0.16844,0.01602],"object_to_goal_dist_end":0.10845,"object_to_goal_dist_start":0.10845,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59754,0.14826,0.16005],"tcp_start":[0.60443,0.15012,0.14068],"tcp_to_object_dist_end":0.14547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":600.0,"object_pos_end":[0.59444,0.16844,0.01602],"object_pos_start":[0.59444,0.16844,0.01602],"object_to_goal_dist_end":0.10845,"object_to_goal_dist_start":0.10845,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":760.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60462,0.15111,0.20315],"tcp_start":[0.59754,0.14826,0.16005],"tcp_to_object_dist_end":0.18821,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```