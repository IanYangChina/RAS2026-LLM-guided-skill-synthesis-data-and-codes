## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0481 | 0.36 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0826 | 0.35 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0525 | 0.37 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0091 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1853 | 0.20 | ❌ rejected |

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

## Current Skill (Q=-0.048) — your mutation base

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
  - 0.15
  weight: 0.3
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: place_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.1
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
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: reach_object
- id: descend_to_object
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_object
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
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: lift_object
- id: transport_to_goal
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal
- id: lower_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lower_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_held_descent
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **lower_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lower_speed: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_held_descent, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.048
- **task_score** (E): 0.361
- **fitness_score**: 0.652  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1030 |
| descend_to_object | 1.00 | 1.00 | 0.1539 |
| grasp | 1.00 | 1.00 | 0.0134 |
| lift | 1.00 | 1.00 | 0.1184 |
| transport_to_goal | 1.00 | 1.00 | 0.1290 |
| lower_to_place | 1.00 | 1.00 | 0.0022 |
| release | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.005, 0.201) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 12.646 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.518, 0.005, 0.201)→(0.521, 0.005, 0.048) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.048)→(0.512, 0.005, 0.037) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.141 | 0.188 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.037)→(0.521, 0.005, 0.156) | (0.526, 0.005, 0.026)→(0.535, 0.005, 0.139) | 0.249→0.195 | 1.00 / 28.000 | 0.100 | 0.478 |
| transport_to_goal | approach | 1.00 / step_budget | (0.554, 0.054, 0.179)→(0.603, 0.163, 0.220) | (0.535, 0.005, 0.139)→(0.607, 0.154, 0.131) | 0.195→0.071 | 1.00 / 15.667 | 50723.737 | 0.852 |
| lower_to_place | descend | 1.00 / step_budget | (0.606, 0.168, 0.234)→(0.606, 0.170, 0.234) | (0.607, 0.154, 0.131)→(0.614, 0.166, 0.045) | 0.071→0.152 | 1.00 / 13.667 | 0.180 | 0.923 |
| release | release | 1.00 / step_budget | (0.606, 0.170, 0.234)→(0.602, 0.168, 0.255) | (0.614, 0.165, 0.046)→(0.610, 0.162, 0.020) | 0.150→0.166 | 1.00 / 3.000 | 0.196 | 0.614 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.573
- phase_score: 0.632
- phase_breakdown.place_goal_score: 0.411
- phase_breakdown.reach_goal_score: 0.673
- phase_breakdown.reach_object_score: 0.750
- phase_breakdown.grasp_object_score: 0.718
- phase_breakdown.lift_object_score: 0.417
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.573
- **Median Q (composite search score)**: -0.080
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.285


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41558,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.27295,"approach_object.approach_tolerance":0.03176,"descend_to_object.descend_speed":0.12151,"descend_to_object.grasp_height":0.0036,"lift.lift_height":0.14888,"lift.lift_speed":0.1261,"lower_to_place.lower_speed":0.11186,"lower_to_place.place_height":0.07101,"release.release_time":0.27211,"transport_to_goal.transport_speed":0.24874,"transport_to_goal.transport_tolerance":0.01896},"optimized_scores":{"best_composite_score":-0.07976,"best_fitness_score":0.62024,"best_task_score":0.30017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":611.0,"contact_point_centroid":[0.62849,0.1184,-0.00358],"force_p95":0.76837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93681,"mean_force":0.20077,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62778,0.13285,0.21922]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54203,0.00052,-0.00133],"force_p95":0.45974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48841,"mean_force":0.09608,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52827,0.00082,0.03907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2775.0,"contact_point_centroid":[0.56958,0.0216,0.1723],"force_p95":0.1778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34304,"mean_force":0.10678,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56403,0.0401,0.17205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5231.0,"contact_point_centroid":[0.53566,-0.01806,0.09286],"force_p95":0.11479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30964,"mean_force":0.0784,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53184,0.00073,0.09076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5417.0,"contact_point_centroid":[0.53551,0.01948,0.09118],"force_p95":0.11268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28872,"mean_force":0.07645,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5317,0.00073,0.08923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3397.0,"contact_point_centroid":[0.57256,0.06228,0.17371],"force_p95":0.14234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27262,"mean_force":0.0893,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56661,0.04412,0.17383]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00102,-0.00203],"force_p95":0.13257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15416,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5305,0.00086,0.03916]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.54431,0.00113,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12355,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51443,0.00038,0.256]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.6285,0.11853,-0.00199],"force_p95":0.12291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12315,"mean_force":0.12261,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64031,0.15248,0.23502]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53317,0.00088,0.12771]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6285,0.11853,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63912,0.15417,0.24291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.5305,-0.01836,0.04043],"force_p95":0.0763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12175,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00084,0.03776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53041,0.01992,0.03956],"force_p95":0.06838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09498,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00084,0.03776]},{"body_a":"left_finger","body_b":"right_finger","contact_count":424.0,"contact_point_centroid":[0.6331,0.13989,0.22488],"force_p95":0.0135,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01095,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63266,0.13989,0.22283]},{"body_a":"left_finger","body_b":"right_finger","contact_count":510.0,"contact_point_centroid":[0.64081,0.1525,0.23734],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01048,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.64031,0.15248,0.23502]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.64172,0.15486,0.24209],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64118,0.15484,0.24001]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.6285,0.11853,0.01602],"final_tcp_position":[0.64225,0.15508,0.24316],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273009.64329,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":528.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53031,0.00079,0.20782],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53821,0.00101,0.04852],"tcp_start":[0.53031,0.00079,0.20782],"tcp_to_object_dist_end":0.02331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00074,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13073,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15416,"subtask_id":"grasp_object","tcp_end":[0.52926,0.00084,0.03772],"tcp_start":[0.53821,0.00101,0.04852],"tcp_to_object_dist_end":0.01907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":395.0,"n_steps_budget":690.0,"object_pos_end":[0.55584,0.0008,0.1368],"object_pos_start":[0.5442,0.00074,0.02587],"object_to_goal_dist_end":0.19003,"object_to_goal_dist_start":0.25051,"object_z_max":0.13656,"peak_contact_force":0.10862,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10725.0,"raw_peak_contact_force":0.48841,"subtask_id":"lift_object","tcp_end":[0.53901,0.00068,0.15564],"tcp_start":[0.52926,0.00084,0.03772],"tcp_to_object_dist_end":0.02527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.62849,0.11846,0.016],"object_pos_start":[0.55584,0.0008,0.1368],"object_to_goal_dist_end":0.18055,"object_to_goal_dist_start":0.19003,"object_z_max":0.16707,"peak_contact_force":0.12317,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7207.0,"raw_peak_contact_force":1.93681,"subtask_id":"reach_goal","tcp_end":[0.63855,0.14932,0.2264],"tcp_start":[0.63813,0.14769,0.227],"tcp_to_object_dist_end":0.21288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.6285,0.11853,0.01602],"object_pos_start":[0.62849,0.11852,0.016],"object_to_goal_dist_end":0.18051,"object_to_goal_dist_start":0.18053,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":990.0,"raw_peak_contact_force":0.12315,"subtask_id":"place_goal","tcp_end":[0.64225,0.15508,0.24316],"tcp_start":[0.64244,0.15477,0.24317],"tcp_to_object_dist_end":0.23047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6285,0.11853,0.01602],"object_pos_start":[0.6285,0.11853,0.01602],"object_to_goal_dist_end":0.18051,"object_to_goal_dist_start":0.18051,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63801,0.15379,0.26197],"tcp_start":[0.64225,0.15508,0.24316],"tcp_to_object_dist_end":0.24865,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86408,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.24829,"approach_object.approach_tolerance":0.01446,"descend_to_object.descend_speed":0.15372,"descend_to_object.grasp_height":0.00408,"lift.lift_height":0.13032,"lift.lift_speed":0.17766,"lower_to_place.lower_speed":0.08305,"lower_to_place.place_height":0.05825,"release.release_time":0.33807,"transport_to_goal.transport_speed":0.28594,"transport_to_goal.transport_tolerance":0.0238},"optimized_scores":{"best_composite_score":0.05643,"best_fitness_score":0.75643,"best_task_score":0.57293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.58265,0.17404,-0.00737],"force_p95":1.21609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41667,"mean_force":0.41032,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58692,0.16788,0.16082]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.5285,0.02878,-0.00141],"force_p95":0.4487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48593,"mean_force":0.09048,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51547,0.02916,0.0402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4380.0,"contact_point_centroid":[0.56473,0.08243,0.14313],"force_p95":0.12939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34103,"mean_force":0.08898,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55914,0.10113,0.14123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4724.0,"contact_point_centroid":[0.52135,0.01018,0.08464],"force_p95":0.1096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30876,"mean_force":0.07187,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51854,0.02908,0.08232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":532.0,"contact_point_centroid":[0.59613,0.18558,0.1492],"force_p95":0.12168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30101,"mean_force":0.07606,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59145,0.16671,0.14881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5050.0,"contact_point_centroid":[0.5211,0.04794,0.0822],"force_p95":0.10803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29953,"mean_force":0.06882,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51834,0.02908,0.08033]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":934.0,"contact_point_centroid":[0.59562,0.18828,0.14762],"force_p95":0.09802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28264,"mean_force":0.06343,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59105,0.16931,0.14743]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.59649,0.14805,0.14941],"force_p95":0.10796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27857,"mean_force":0.07391,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.59147,0.16674,0.14884]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03057,-0.00213],"force_p95":0.16075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22532,"mean_force":0.13272,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51766,0.02932,0.04006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.59551,0.15053,0.14767],"force_p95":0.09215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22527,"mean_force":0.05578,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59113,0.16934,0.14757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5070.0,"contact_point_centroid":[0.56474,0.11949,0.1423],"force_p95":0.11575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22146,"mean_force":0.07901,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55901,0.10102,0.14112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.51735,0.01003,0.04148],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15128,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51648,0.02924,0.03873]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.13648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51038,0.01264,0.246]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52319,0.02792,0.12079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.51729,0.04839,0.04052],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07805,"mean_force":0.0445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51649,0.02924,0.03873]}],"total_contact_groups":15},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58737,0.166,0.02672],"final_tcp_position":[0.59288,0.16951,0.15077],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":37.69355,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":37.69355,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52287,0.02619,0.19127],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52524,0.0298,0.04906],"tcp_start":[0.52287,0.02619,0.19127],"tcp_to_object_dist_end":0.02365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.02948,0.02554],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18466,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15373,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10882.0,"raw_peak_contact_force":0.22532,"subtask_id":"grasp_object","tcp_end":[0.51645,0.02924,0.03869],"tcp_start":[0.52524,0.0298,0.04906],"tcp_to_object_dist_end":0.0192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":324.0,"n_steps_budget":600.0,"object_pos_end":[0.54149,0.0295,0.11869],"object_pos_start":[0.53044,0.02948,0.02554],"object_to_goal_dist_end":0.16107,"object_to_goal_dist_start":0.18466,"object_z_max":0.11844,"peak_contact_force":0.1086,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9855.0,"raw_peak_contact_force":0.48593,"subtask_id":"lift_object","tcp_end":[0.52497,0.02918,0.13664],"tcp_start":[0.51645,0.02924,0.03869],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.59761,0.16472,0.1215],"object_pos_start":[0.54149,0.0295,0.11869],"object_to_goal_dist_end":0.01968,"object_to_goal_dist_start":0.16107,"object_z_max":0.12148,"peak_contact_force":0.09499,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9450.0,"raw_peak_contact_force":0.34103,"subtask_id":"reach_goal","tcp_end":[0.59128,0.16458,0.14859],"tcp_start":[0.52497,0.02918,0.13664],"tcp_to_object_dist_end":0.02783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":38.0,"n_steps_budget":1000.0,"object_pos_end":[0.59914,0.16969,0.12374],"object_pos_start":[0.59761,0.16472,0.1215],"object_to_goal_dist_end":0.01816,"object_to_goal_dist_start":0.01968,"object_z_max":0.12361,"peak_contact_force":0.09305,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.30101,"subtask_id":"place_goal","tcp_end":[0.59288,0.16951,0.15077],"tcp_start":[0.59128,0.16458,0.14859],"tcp_to_object_dist_end":0.02774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58737,0.166,0.02672],"object_pos_start":[0.59914,0.16969,0.12374],"object_to_goal_dist_end":0.08355,"object_to_goal_dist_start":0.01816,"object_z_max":0.1238,"peak_contact_force":0.34166,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2058.0,"raw_peak_contact_force":1.41667,"tcp_end":[0.58683,0.16786,0.17172],"tcp_start":[0.59288,0.16951,0.15077],"tcp_to_object_dist_end":0.14501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35079,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.30644,"approach_object.approach_tolerance":0.02641,"descend_to_object.descend_speed":0.1904,"descend_to_object.grasp_height":0.0002,"lift.lift_height":0.16798,"lift.lift_speed":0.03526,"lower_to_place.lower_speed":0.09757,"lower_to_place.place_height":0.07998,"release.release_time":0.41955,"transport_to_goal.transport_speed":0.27251,"transport_to_goal.transport_tolerance":0.03084},"optimized_scores":{"best_composite_score":-0.12099,"best_fitness_score":0.57901,"best_task_score":0.2099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.61394,0.20185,-0.01103],"force_p95":1.87311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34623,"mean_force":0.70822,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.58311,0.18374,0.30854]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.49985,-0.01474,-0.00149],"force_p95":0.44693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4596,"mean_force":0.18808,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4899,-0.01497,0.0369]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61413,0.20236,-0.00242],"force_p95":0.13178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30398,"mean_force":0.11493,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58094,0.18326,0.3105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7637.0,"contact_point_centroid":[0.53481,0.04629,0.21988],"force_p95":0.1319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27813,"mean_force":0.07565,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53165,0.0652,0.21818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10016.0,"contact_point_centroid":[0.49272,0.00427,0.10332],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27033,"mean_force":0.052,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4929,-0.01491,0.10118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10459.0,"contact_point_centroid":[0.49271,-0.03405,0.10377],"force_p95":0.07361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25564,"mean_force":0.05039,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49296,-0.01491,0.10195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.58604,0.19198,0.28141],"force_p95":0.17922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24568,"mean_force":0.05513,"phase_index":5.0,"phase_name":"lower_to_place","phase_type":"descend","tcp_position_centroid":[0.57977,0.17614,0.28358]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9094.0,"contact_point_centroid":[0.53723,0.09015,0.22313],"force_p95":0.1029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22124,"mean_force":0.06457,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53431,0.07145,0.22177]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.0155,-0.00206],"force_p95":0.1411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18388,"mean_force":0.12763,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01499,0.03722]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.50382,-0.01567,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5002,-0.00545,0.25477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49134,0.00423,0.03879],"force_p95":0.07783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12951,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01498,0.03602]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49917,-0.01331,0.12516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4920.0,"contact_point_centroid":[0.49139,-0.03407,0.03787],"force_p95":0.06992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0811,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49088,-0.01498,0.03602]},{"body_a":"left_finger","body_b":"right_finger","contact_count":207.0,"contact_point_centroid":[0.58272,0.18389,0.30859],"force_p95":0.0153,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01115,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58224,0.18387,0.30642]}],"total_contact_groups":14},"final_pose_error":0.01937,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.61413,0.20247,0.01602],"final_tcp_position":[0.5831,0.18412,0.30939],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":152170.99322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":580.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5007,-0.01161,0.20536],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49939,-0.01506,0.04536],"tcp_start":[0.5007,-0.01161,0.20536],"tcp_to_object_dist_end":0.01985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01495,0.02578],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31196,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13743,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.18388,"subtask_id":"grasp_object","tcp_end":[0.49085,-0.01498,0.03599],"tcp_start":[0.49939,-0.01506,0.04536],"tcp_to_object_dist_end":0.01643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50881,-0.01493,0.16095],"object_pos_start":[0.50372,-0.01495,0.02578],"object_to_goal_dist_end":0.23378,"object_to_goal_dist_start":0.31196,"object_z_max":0.16069,"peak_contact_force":0.08137,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20567.0,"raw_peak_contact_force":0.4596,"subtask_id":"lift_object","tcp_end":[0.49907,-0.01489,0.17441],"tcp_start":[0.49085,-0.01498,0.03599],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.59363,0.17849,0.25489],"object_pos_start":[0.50881,-0.01493,0.16095],"object_to_goal_dist_end":0.01309,"object_to_goal_dist_start":0.23378,"object_z_max":0.25529,"peak_contact_force":152170.99322,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16731.0,"raw_peak_contact_force":0.27813,"subtask_id":"reach_goal","tcp_end":[0.57993,0.1757,0.28361],"tcp_start":[0.49907,-0.01489,0.17441],"tcp_to_object_dist_end":0.03195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.61426,0.20837,-0.00557],"object_pos_start":[0.59363,0.17849,0.25489],"object_to_goal_dist_end":0.25601,"object_to_goal_dist_start":0.01309,"object_z_max":0.25489,"peak_contact_force":0.32543,"phase_name":"lower_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":197.0,"raw_peak_contact_force":2.34623,"subtask_id":"place_goal","tcp_end":[0.5831,0.18412,0.30939],"tcp_start":[0.58329,0.18372,0.30895],"tcp_to_object_dist_end":0.31743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61413,0.20247,0.01602],"object_pos_start":[0.6141,0.20749,-0.00083],"object_to_goal_dist_end":0.23417,"object_to_goal_dist_start":0.25123,"object_z_max":0.01702,"peak_contact_force":0.12265,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1007.0,"raw_peak_contact_force":0.30398,"tcp_end":[0.58026,0.18291,0.33018],"tcp_start":[0.5831,0.18412,0.30939],"tcp_to_object_dist_end":0.31659,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```