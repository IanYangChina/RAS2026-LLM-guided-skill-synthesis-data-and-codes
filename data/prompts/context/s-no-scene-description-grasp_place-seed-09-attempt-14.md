## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.3002 | 0.19 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 7 | 0.1120 | 0.36 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0916 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0128 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3728 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.300) — your mutation base

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

- **Composite score**: -0.300
- **task_score** (E): 0.192
- **fitness_score**: 0.170  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1636 |
| descend_to_grasp | 0.00 | 1.00 | 0.1026 |
| grasp | 1.00 | 1.00 | 0.0008 |
| lift | 0.33 | 1.00 | 0.1264 |
| transport | 1.00 | 1.00 | 0.2242 |
| descend_to_place | 0.00 | 1.00 | 0.0308 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.426, -0.011, 0.158) | (0.515, -0.017, 0.030)→(0.476, -0.017, 0.016) | 0.268→0.294 | 1.00 / 5.000 | 256.778 | 1478.240 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.426, -0.011, 0.158)→(0.502, -0.050, 0.198) | (0.476, -0.017, 0.016)→(0.476, -0.017, 0.016) | 0.294→0.294 | 1.00 / 6.000 | 322.961 | 922.848 |
| grasp | grasp | 1.00 / step_budget | (0.502, -0.050, 0.198)→(0.502, -0.050, 0.197) | (0.476, -0.017, 0.016)→(0.476, -0.017, 0.016) | 0.294→0.294 | 1.00 / 9.667 | 68.513 | 325.408 |
| lift | lift | 0.33 / step_budget | (0.502, -0.050, 0.197)→(0.498, -0.004, 0.282) | (0.476, -0.017, 0.016)→(0.467, -0.010, 0.015) | 0.294→0.292 | 1.00 / 9.667 | 56116.013 | 436.505 |
| transport | approach | 1.00 / step_budget | (0.498, -0.004, 0.282)→(0.613, 0.167, 0.319) | (0.467, -0.010, 0.015)→(0.471, 0.060, 0.016) | 0.292→0.248 | 1.00 / 8.333 | 6627.273 | 365.402 |
| descend_to_place | descend | 0.00 / step_budget | (0.613, 0.167, 0.319)→(0.623, 0.178, 0.294) | (0.471, 0.060, 0.016)→(0.471, 0.060, 0.016) | 0.248→0.248 | 1.00 / 9.333 | 91195.822 | 694.143 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.209
- phase_score: 0.105
- phase_breakdown.lift_object_score: 0.103
- phase_breakdown.reach_object_score: 0.158
- phase_breakdown.place_object_score: 0.096
- grasp_place_fitness: 0.194

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.194
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.209
- **Median Q (composite search score)**: -0.280
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.243


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.00427,"average_mean_iterations":4.9359,"average_solve_count":234.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.19628,"descend_to_grasp.descend_speed":0.10261,"descend_to_place.descend_place_speed":0.07364,"descend_to_place.place_z_offset":0.00752,"lift.lift_height":0.26902,"lift.lift_speed":0.07258,"transport.transport_speed":0.04607},"optimized_scores":{"best_composite_score":-0.34451,"best_fitness_score":0.12549,"best_task_score":0.16806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":835.0,"contact_point_centroid":[0.65039,-0.00803,-0.00041],"force_p95":434.91227,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1485.61882,"mean_force":240.10114,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42968,-0.00877,0.15384]},{"body_a":"world","body_b":"link6","contact_count":776.0,"contact_point_centroid":[0.63503,-0.08192,-0.00018],"force_p95":575.50559,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":865.92609,"mean_force":370.46956,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53071,-0.02953,0.25418]},{"body_a":"world","body_b":"link6","contact_count":899.0,"contact_point_centroid":[0.61064,0.21904,-0.00033],"force_p95":482.3969,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":765.69878,"mean_force":372.33968,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6127,0.22482,0.29364]},{"body_a":"link5","body_b":"hand","contact_count":569.0,"contact_point_centroid":[0.51538,-0.13116,0.23253],"force_p95":333.73763,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":668.33444,"mean_force":252.17046,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5476,-0.03992,0.27545]},{"body_a":"world","body_b":"link6","contact_count":445.0,"contact_point_centroid":[0.67365,-0.10996,-0.00013],"force_p95":83.27991,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":537.28524,"mean_force":72.88856,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.57596,-0.0654,0.27121]},{"body_a":"world","body_b":"link6","contact_count":629.0,"contact_point_centroid":[0.53438,-0.0619,-0.00012],"force_p95":264.25861,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":412.27087,"mean_force":195.39991,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53114,-0.05496,0.29355]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53938,-0.00042,-0.00356],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.44186,"mean_force":17.92918,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38677,-0.00368,0.04695]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.48888,-0.03841,-0.0001],"force_p95":122.68036,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.53026,"mean_force":96.57203,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5058,-0.03151,0.29372]},{"body_a":"link5","body_b":"hand","contact_count":450.0,"contact_point_centroid":[0.54194,-0.15664,0.21737],"force_p95":36.37217,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.98247,"mean_force":28.8643,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.57596,-0.0654,0.27122]},{"body_a":"grasp_target","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.50984,-0.02387,0.03785],"force_p95":3.82065,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.23305,"mean_force":0.90514,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3988,-0.00392,0.08928]},{"body_a":"grasp_target","body_b":"hand","contact_count":144.0,"contact_point_centroid":[0.50181,-0.0294,0.05036],"force_p95":2.20066,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.35148,"mean_force":0.89843,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39801,-0.00388,0.08715]},{"body_a":"world","body_b":"grasp_target","contact_count":3532.0,"contact_point_centroid":[0.5063,-0.02484,-0.00229],"force_p95":0.28375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33459,"mean_force":0.15764,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44206,-0.00852,0.16534]},{"body_a":"grasp_target","body_b":"link6","contact_count":567.0,"contact_point_centroid":[0.51308,-0.02802,0.02614],"force_p95":0.73752,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.98597,"mean_force":0.55246,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52647,-0.05206,0.29418]},{"body_a":"world","body_b":"grasp_target","contact_count":2259.0,"contact_point_centroid":[0.48627,-0.01815,-0.00301],"force_p95":0.50318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00636,"mean_force":0.24626,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53565,-0.05805,0.29295]},{"body_a":"grasp_target","body_b":"link6","contact_count":426.0,"contact_point_centroid":[0.50349,0.03506,0.02408],"force_p95":0.84817,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.90852,"mean_force":0.50456,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.533,0.0361,0.30556]},{"body_a":"world","body_b":"grasp_target","contact_count":2362.0,"contact_point_centroid":[0.47866,0.06903,-0.0037],"force_p95":0.64088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85815,"mean_force":0.24969,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56016,0.10304,0.32084]}],"total_contact_groups":25},"final_pose_error":0.07904,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.47968,0.09409,0.01602],"final_tcp_position":[0.61762,0.22889,0.29362],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.02175,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.49907,-0.02539,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33629,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":388.95896,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4814.0,"raw_peak_contact_force":1485.61882,"tcp_end":[0.46451,-0.02116,0.16662],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15457,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":815.0,"n_steps_budget":960.0,"object_pos_end":[0.49907,-0.02539,0.01602],"object_pos_start":[0.49907,-0.02539,0.01602],"object_to_goal_dist_end":0.33629,"object_to_goal_dist_start":0.33629,"object_z_max":0.01602,"peak_contact_force":370.07626,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4605.0,"raw_peak_contact_force":865.92609,"subtask_id":"reach_object","tcp_end":[0.5757,-0.06522,0.27108],"tcp_start":[0.46451,-0.02116,0.16662],"tcp_to_object_dist_end":0.26929,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49907,-0.02539,0.01602],"object_pos_start":[0.49907,-0.02539,0.01602],"object_to_goal_dist_end":0.33629,"object_to_goal_dist_start":0.33629,"object_z_max":0.01602,"peak_contact_force":68.10256,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3040.0,"raw_peak_contact_force":537.28524,"tcp_end":[0.576,-0.06539,0.27122],"tcp_start":[0.5757,-0.06522,0.27108],"tcp_to_object_dist_end":0.26953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.47355,-0.00354,0.01445],"object_pos_start":[0.49907,-0.02539,0.01602],"object_to_goal_dist_end":0.33081,"object_to_goal_dist_start":0.33629,"object_z_max":0.01606,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6482.0,"raw_peak_contact_force":412.27087,"subtask_id":"lift_object","tcp_end":[0.50561,-0.03153,0.29364],"tcp_start":[0.576,-0.06539,0.27122],"tcp_to_object_dist_end":0.28241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.47968,0.09409,0.01602],"object_pos_start":[0.47355,-0.00354,0.01445],"object_to_goal_dist_end":0.26751,"object_to_goal_dist_start":0.33081,"object_z_max":0.01948,"peak_contact_force":9749.16473,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6186.0,"raw_peak_contact_force":128.53026,"tcp_end":[0.60466,0.21263,0.34601],"tcp_start":[0.50561,-0.03153,0.29364],"tcp_to_object_dist_end":0.37224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47968,0.09409,0.01602],"object_pos_start":[0.47968,0.09409,0.01602],"object_to_goal_dist_end":0.26751,"object_to_goal_dist_start":0.26751,"object_z_max":0.01602,"peak_contact_force":273006.02175,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9229.0,"raw_peak_contact_force":765.69878,"subtask_id":"place_object","tcp_end":[0.61762,0.22889,0.29362],"tcp_start":[0.60466,0.21263,0.34601],"tcp_to_object_dist_end":0.33803,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.95152,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.04456,"descend_to_grasp.descend_speed":0.04737,"descend_to_place.descend_place_speed":0.04867,"descend_to_place.place_z_offset":0.02325,"lift.lift_height":0.16172,"lift.lift_speed":0.05365,"transport.transport_speed":0.13529},"optimized_scores":{"best_composite_score":-0.27588,"best_fitness_score":0.19412,"best_task_score":0.20907},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.64354,-0.00694,-0.00048],"force_p95":196.97769,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1486.16323,"mean_force":198.44329,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40726,-0.00688,0.13125]},{"body_a":"world","body_b":"link6","contact_count":979.0,"contact_point_centroid":[0.63607,-0.01365,-0.00022],"force_p95":518.448,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":887.33459,"mean_force":294.60353,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43633,-0.02534,0.18887]},{"body_a":"world","body_b":"link6","contact_count":949.0,"contact_point_centroid":[0.62641,0.15505,-0.00033],"force_p95":439.86535,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":723.59721,"mean_force":326.67271,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63303,0.15719,0.29366]},{"body_a":"link5","body_b":"hand","contact_count":302.0,"contact_point_centroid":[0.49313,-0.14299,0.25138],"force_p95":285.3492,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":494.11868,"mean_force":173.6042,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54411,-0.05112,0.2869]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53888,-0.00093,-0.00379],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":486.03897,"mean_force":22.09268,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38495,-0.00456,0.04849]},{"body_a":"world","body_b":"link6","contact_count":469.0,"contact_point_centroid":[0.58102,-0.09031,-0.00023],"force_p95":341.42784,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":465.02749,"mean_force":285.17458,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51494,-0.03654,0.25733]},{"body_a":"world","body_b":"link6","contact_count":79.0,"contact_point_centroid":[0.54412,-0.06844,-4e-05],"force_p95":284.36908,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.03759,"mean_force":189.25277,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55576,-0.04886,0.29305]},{"body_a":"link5","body_b":"hand","contact_count":259.0,"contact_point_centroid":[0.52321,0.02626,0.18531],"force_p95":165.2936,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.09583,"mean_force":81.27003,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46378,-0.06103,0.17874]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.68251,-0.02107,-0.00012],"force_p95":74.3518,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.71053,"mean_force":70.05151,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46569,-0.06374,0.16026]},{"body_a":"link5","body_b":"hand","contact_count":126.0,"contact_point_centroid":[0.52342,0.02636,0.17884],"force_p95":36.93149,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.52334,"mean_force":7.18134,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46572,-0.06372,0.16049]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.49417,-0.14719,0.24761],"force_p95":28.07237,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.02632,"mean_force":8.25658,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54919,-0.05824,0.2901]},{"body_a":"grasp_target","body_b":"link7","contact_count":467.0,"contact_point_centroid":[0.52994,-0.01681,0.03383],"force_p95":1.12879,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.38677,"mean_force":0.36252,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4012,-0.00539,0.11089]},{"body_a":"grasp_target","body_b":"link6","contact_count":140.0,"contact_point_centroid":[0.54675,-0.01378,0.02574],"force_p95":0.75,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.28712,"mean_force":0.41604,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39354,-0.0047,0.09034]},{"body_a":"world","body_b":"grasp_target","contact_count":3645.0,"contact_point_centroid":[0.51309,-0.02869,-0.0023],"force_p95":0.3109,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33276,"mean_force":0.15995,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42008,-0.00659,0.1436]},{"body_a":"grasp_target","body_b":"hand","contact_count":133.0,"contact_point_centroid":[0.50006,-0.0337,0.04827],"force_p95":2.43393,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.00767,"mean_force":0.97602,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39481,-0.00466,0.08366]},{"body_a":"grasp_target","body_b":"link6","contact_count":422.0,"contact_point_centroid":[0.5346,0.00015,0.0248],"force_p95":1.07789,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.15262,"mean_force":0.62941,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57663,0.01229,0.2975]}],"total_contact_groups":25},"final_pose_error":0.09386,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50944,0.04662,0.01602],"final_tcp_position":[0.63629,0.16024,0.29385],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.93298,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,-0.02868,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28152,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":190.26947,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5293.0,"raw_peak_contact_force":1486.16323,"tcp_end":[0.42115,-0.01039,0.16688],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,-0.02868,0.01602],"object_pos_start":[0.50683,-0.02868,0.01602],"object_to_goal_dist_end":0.28152,"object_to_goal_dist_start":0.28152,"object_z_max":0.01602,"peak_contact_force":213.64833,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5238.0,"raw_peak_contact_force":887.33459,"subtask_id":"reach_object","tcp_end":[0.46578,-0.06336,0.16136],"tcp_start":[0.42115,-0.01039,0.16688],"tcp_to_object_dist_end":0.15495,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50683,-0.02868,0.01602],"object_pos_start":[0.50683,-0.02868,0.01602],"object_to_goal_dist_end":0.28152,"object_to_goal_dist_start":0.28152,"object_z_max":0.01602,"peak_contact_force":69.03908,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2718.0,"raw_peak_contact_force":200.71053,"tcp_end":[0.46567,-0.06379,0.16014],"tcp_start":[0.46578,-0.06336,0.16136],"tcp_to_object_dist_end":0.15394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":523.0,"n_steps_budget":690.0,"object_pos_end":[0.50683,-0.02868,0.01602],"object_pos_start":[0.50683,-0.02868,0.01602],"object_to_goal_dist_end":0.28152,"object_to_goal_dist_start":0.28152,"object_z_max":0.01602,"peak_contact_force":312.37262,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5177.0,"raw_peak_contact_force":494.11868,"subtask_id":"lift_object","tcp_end":[0.54902,-0.05784,0.2897],"tcp_start":[0.46567,-0.06379,0.16014],"tcp_to_object_dist_end":0.27845,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.50944,0.04662,0.01602],"object_pos_start":[0.50683,-0.02868,0.01602],"object_to_goal_dist_end":0.23477,"object_to_goal_dist_start":0.28152,"object_z_max":0.01727,"peak_contact_force":9748.93298,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5193.0,"raw_peak_contact_force":293.03759,"tcp_end":[0.62705,0.14934,0.3162],"tcp_start":[0.54902,-0.05784,0.2897],"tcp_to_object_dist_end":0.33837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50944,0.04662,0.01602],"object_pos_start":[0.50944,0.04662,0.01602],"object_to_goal_dist_end":0.23477,"object_to_goal_dist_start":0.23477,"object_z_max":0.01602,"peak_contact_force":273.04477,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9281.0,"raw_peak_contact_force":723.59721,"subtask_id":"place_object","tcp_end":[0.63629,0.16024,0.29385],"tcp_start":[0.62705,0.14934,0.3162],"tcp_to_object_dist_end":0.32587,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.00613,"average_mean_iterations":8.13497,"average_solve_count":163.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.06823,"descend_to_grasp.descend_speed":0.05848,"descend_to_place.descend_place_speed":0.0491,"descend_to_place.place_z_offset":0.04421,"lift.lift_height":0.17948,"lift.lift_speed":0.03299,"transport.transport_speed":0.11742},"optimized_scores":{"best_composite_score":-0.28033,"best_fitness_score":0.18967,"best_task_score":0.19818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63031,-3e-05,-0.00048],"force_p95":196.37139,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1462.9367,"mean_force":200.26605,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38602,-0.00012,0.11717]},{"body_a":"world","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.63168,0.00477,-0.00021],"force_p95":460.36431,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1015.28421,"mean_force":287.17838,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43167,0.00016,0.18792]},{"body_a":"world","body_b":"link6","contact_count":807.0,"contact_point_centroid":[0.53207,0.05119,-0.00013],"force_p95":534.63837,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":674.63848,"mean_force":412.8987,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53048,0.06885,0.29221]},{"body_a":"link5","body_b":"hand","contact_count":288.0,"contact_point_centroid":[0.43157,-0.05204,0.24985],"force_p95":491.58817,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":643.90904,"mean_force":260.18424,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48092,0.0231,0.29144]},{"body_a":"world","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.60572,0.1379,-0.00033],"force_p95":376.49862,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":593.13323,"mean_force":322.96781,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61152,0.14256,0.29368]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52499,0.00404,-0.00342],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":472.51422,"mean_force":21.47792,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37112,-0.00025,0.04937]},{"body_a":"world","body_b":"link6","contact_count":867.0,"contact_point_centroid":[0.58329,-0.01834,-0.00017],"force_p95":297.55598,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.12439,"mean_force":243.35958,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45295,0.10051,0.20706]},{"body_a":"world","body_b":"link6","contact_count":448.0,"contact_point_centroid":[0.68185,0.01944,-0.00013],"force_p95":71.86181,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.22819,"mean_force":70.16414,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46473,-0.02143,0.1603]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.44366,0.01194,0.04153],"force_p95":3.55937,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91623,"mean_force":1.64634,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38222,-0.00021,0.05001]},{"body_a":"world","body_b":"grasp_target","contact_count":3932.0,"contact_point_centroid":[0.42667,0.00187,-0.00212],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3148,"mean_force":0.13793,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39839,-9e-05,0.12729]},{"body_a":"grasp_target","body_b":"link6","contact_count":314.0,"contact_point_centroid":[0.45059,-0.00132,0.03505],"force_p95":0.43815,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.18094,"mean_force":0.32905,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48868,0.02099,0.29282]},{"body_a":"world","body_b":"grasp_target","contact_count":3161.0,"contact_point_centroid":[0.42264,0.02699,-0.00251],"force_p95":0.41946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86518,"mean_force":0.16441,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53248,0.07422,0.29178]},{"body_a":"grasp_target","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.4741,0.00386,0.00933],"force_p95":0.67218,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72392,"mean_force":0.27626,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3701,-0.00026,0.04701]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42167,0.00216,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43246,0.00011,0.18775]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.42167,0.00216,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46473,-0.02143,0.1603]},{"body_a":"world","body_b":"grasp_target","contact_count":3648.0,"contact_point_centroid":[0.42167,0.00216,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45283,0.09777,0.2065]}],"total_contact_groups":21},"final_pose_error":0.12758,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42283,0.0407,0.01602],"final_tcp_position":[0.61417,0.14632,0.29375],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1462.9367,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42167,0.00216,0.01602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.26364,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":191.10417,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4892.0,"raw_peak_contact_force":1462.9367,"tcp_end":[0.39104,-0.00013,0.1394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12714,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42167,0.00216,0.01602],"object_pos_start":[0.42167,0.00216,0.01602],"object_to_goal_dist_end":0.26364,"object_to_goal_dist_start":0.26364,"object_z_max":0.01602,"peak_contact_force":385.15713,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4975.0,"raw_peak_contact_force":1015.28421,"subtask_id":"reach_object","tcp_end":[0.46469,-0.02148,0.16102],"tcp_start":[0.39104,-0.00013,0.1394],"tcp_to_object_dist_end":0.15308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42167,0.00216,0.01602],"object_pos_start":[0.42167,0.00216,0.01602],"object_to_goal_dist_end":0.26364,"object_to_goal_dist_start":0.26364,"object_z_max":0.01602,"peak_contact_force":68.3961,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2597.0,"raw_peak_contact_force":238.22819,"tcp_end":[0.46471,-0.02142,0.16019],"tcp_start":[0.46469,-0.02148,0.16102],"tcp_to_object_dist_end":0.15229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":912.0,"n_steps_budget":1000.0,"object_pos_end":[0.42167,0.00216,0.01602],"object_pos_start":[0.42167,0.00216,0.01602],"object_to_goal_dist_end":0.26364,"object_to_goal_dist_start":0.26364,"object_z_max":0.01602,"peak_contact_force":83.93709,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8413.0,"raw_peak_contact_force":403.12439,"subtask_id":"lift_object","tcp_end":[0.44049,0.07677,0.26232],"tcp_start":[0.46471,-0.02142,0.16019],"tcp_to_object_dist_end":0.25804,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.42283,0.0407,0.01602],"object_pos_start":[0.42167,0.00216,0.01602],"object_to_goal_dist_end":0.24278,"object_to_goal_dist_start":0.26364,"object_z_max":0.01791,"peak_contact_force":383.72238,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8351.0,"raw_peak_contact_force":674.63848,"tcp_end":[0.60732,0.13976,0.29381],"tcp_start":[0.44049,0.07677,0.26232],"tcp_to_object_dist_end":0.34788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42283,0.0407,0.01602],"object_pos_start":[0.42283,0.0407,0.01602],"object_to_goal_dist_end":0.24278,"object_to_goal_dist_start":0.24278,"object_z_max":0.01602,"peak_contact_force":308.40028,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9301.0,"raw_peak_contact_force":593.13323,"subtask_id":"place_object","tcp_end":[0.61417,0.14632,0.29375],"tcp_start":[0.60732,0.13976,0.29381],"tcp_to_object_dist_end":0.35342,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```