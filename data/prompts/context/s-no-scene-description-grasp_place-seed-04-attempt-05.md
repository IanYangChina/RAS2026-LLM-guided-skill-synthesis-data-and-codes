## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0091 | 0.36 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1853 | 0.20 | ❌ rejected |
| 3 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0329 | 0.20 | ❌ rejected |

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

## Current Skill (Q=-0.009) — your mutation base

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
  - 0.03
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
- id: approach_goal
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
    approach_goal_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: reach_goal
- id: descend_to_goal
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
    - 0.025
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
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
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.025], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.009
- **task_score** (E): 0.357
- **fitness_score**: 0.641  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0974 |
| descend_to_object | 1.00 | 1.00 | 0.1512 |
| grasp | 1.00 | 1.00 | 0.0134 |
| lift | 1.00 | 1.00 | 0.1530 |
| approach_goal | 1.00 | 0.67 | 0.2189 |
| descend_to_goal | 1.00 | 0.67 | 0.0842 |
| release | 1.00 | 1.00 | 0.0195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.004, 0.207) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.518, 0.004, 0.207)→(0.521, 0.005, 0.056) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.521, 0.005, 0.056)→(0.512, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 42.667 | 0.148 | 0.193 |
| lift | lift | 1.00 / step_budget | (0.512, 0.005, 0.046)→(0.522, 0.005, 0.198) | (0.526, 0.005, 0.026)→(0.530, 0.005, 0.174) | 0.249→0.198 | 1.00 / 38.000 | 0.078 | 0.396 |
| approach_goal | approach | 1.00 / step_budget | (0.522, 0.005, 0.198)→(0.605, 0.164, 0.317) | (0.530, 0.005, 0.174)→(0.607, 0.167, 0.149) | 0.198→0.122 | 0.67 / 9.000 | 0.091 | 0.898 |
| descend_to_goal | descend | 1.00 / step_budget | (0.605, 0.164, 0.317)→(0.608, 0.171, 0.233) | (0.607, 0.167, 0.149)→(0.605, 0.182, 0.033) | 0.122→0.152 | 0.67 / 5.667 | 94251.536 | 1.031 |
| release | release | 1.00 / step_budget | (0.608, 0.171, 0.233)→(0.603, 0.170, 0.252) | (0.605, 0.182, 0.033)→(0.605, 0.183, 0.019) | 0.152→0.166 | 1.00 / 4.000 | 0.123 | 0.559 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.538
- phase_score: 0.588
- phase_breakdown.place_goal_score: 0.308
- phase_breakdown.reach_goal_score: 0.672
- phase_breakdown.reach_object_score: 0.496
- phase_breakdown.grasp_object_score: 0.662
- phase_breakdown.lift_object_score: 0.712
- grasp_place_fitness: 0.731

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.731
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.538
- **Median Q (composite search score)**: -0.025
- **K-run variance**: 0.0046
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.379


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45794,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.22644,"approach_object.approach_speed":0.07154,"approach_object.approach_tolerance":0.01759,"descend_to_goal.descend_goal_speed":0.19514,"descend_to_goal.place_height":0.023,"descend_to_object.descend_speed":0.11913,"descend_to_object.grasp_height":0.01001,"lift.lift_height":0.2437,"lift.lift_speed":0.04242,"release.release_time":0.26055},"optimized_scores":{"best_composite_score":-0.02522,"best_fitness_score":0.62478,"best_task_score":0.32149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":350.0,"contact_point_centroid":[0.64362,0.20102,-0.00612],"force_p95":1.23402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55397,"mean_force":0.30249,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.64186,0.15219,0.26474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6445.0,"contact_point_centroid":[0.57807,0.0377,0.27584],"force_p95":0.13865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51155,"mean_force":0.07191,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57703,0.05663,0.27666]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.54098,0.00081,-0.00144],"force_p95":0.37206,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39472,"mean_force":0.14083,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52869,0.00083,0.04505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14813.0,"contact_point_centroid":[0.53338,-0.01837,0.14755],"force_p95":0.07829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26737,"mean_force":0.05471,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53296,0.00075,0.14536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15209.0,"contact_point_centroid":[0.53374,0.01985,0.14862],"force_p95":0.07773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25264,"mean_force":0.05354,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53304,0.00075,0.14638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7468.0,"contact_point_centroid":[0.58092,0.07955,0.27811],"force_p95":0.11551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2467,"mean_force":0.06311,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57992,0.0609,0.27894]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64051,0.19898,-0.00199],"force_p95":0.15397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2034,"mean_force":0.12359,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63975,0.15377,0.23113]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13232,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15404,"mean_force":0.12547,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53092,0.00088,0.04552]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5156,0.00043,0.24777]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53522,0.00095,0.12483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.53078,-0.01834,0.04681],"force_p95":0.0763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11885,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52972,0.00086,0.04412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53072,0.01993,0.04593],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09383,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52972,0.00086,0.04412]},{"body_a":"left_finger","body_b":"right_finger","contact_count":321.0,"contact_point_centroid":[0.64294,0.15286,0.25837],"force_p95":0.01347,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.0112,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.64227,0.15284,0.25632]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.64252,0.15447,0.22976],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64178,0.15445,0.22768]}],"total_contact_groups":14},"final_pose_error":0.01957,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64047,0.19896,0.02602],"final_tcp_position":[0.64347,0.1548,0.23294],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.69963,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53381,0.0009,0.19376],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53856,0.00102,0.05493],"tcp_start":[0.53381,0.0009,0.19376],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13069,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15404,"subtask_id":"grasp_object","tcp_end":[0.52969,0.00086,0.04408],"tcp_start":[0.53856,0.00102,0.05493],"tcp_to_object_dist_end":0.0233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.54755,0.00083,0.22606],"object_pos_start":[0.54421,0.00077,0.02586],"object_to_goal_dist_end":0.18965,"object_to_goal_dist_start":0.25049,"object_z_max":0.22581,"peak_contact_force":0.07506,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30114.0,"raw_peak_contact_force":0.39472,"subtask_id":"lift_object","tcp_end":[0.54048,0.00071,0.25015],"tcp_start":[0.52969,0.00086,0.04408],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.64022,0.16787,0.2209],"object_pos_start":[0.54755,0.00083,0.22606],"object_to_goal_dist_end":0.03223,"object_to_goal_dist_start":0.18965,"object_z_max":0.27932,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13913.0,"raw_peak_contact_force":0.51155,"subtask_id":"reach_goal","tcp_end":[0.6394,0.14759,0.32646],"tcp_start":[0.54048,0.00071,0.25015],"tcp_to_object_dist_end":0.10749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.64089,0.19914,0.02634],"object_pos_start":[0.64022,0.16787,0.2209],"object_to_goal_dist_end":0.16994,"object_to_goal_dist_start":0.03223,"object_z_max":0.2209,"peak_contact_force":9748.69963,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":671.0,"raw_peak_contact_force":2.55397,"subtask_id":"place_goal","tcp_end":[0.64347,0.1548,0.23294],"tcp_start":[0.6394,0.14759,0.32646],"tcp_to_object_dist_end":0.21132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64047,0.19896,0.02602],"object_pos_start":[0.64089,0.19914,0.02634],"object_to_goal_dist_end":0.17022,"object_to_goal_dist_start":0.16994,"object_z_max":0.02634,"peak_contact_force":0.1232,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.2034,"subtask_id":"place_goal","tcp_end":[0.63859,0.15337,0.25034],"tcp_start":[0.64347,0.1548,0.23294],"tcp_to_object_dist_end":0.22892,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63855,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.19504,"approach_object.approach_speed":0.24587,"approach_object.approach_tolerance":0.0357,"descend_to_goal.descend_goal_speed":0.15435,"descend_to_goal.place_height":0.04954,"descend_to_object.descend_speed":0.09363,"descend_to_object.grasp_height":0.01075,"lift.lift_height":0.15772,"lift.lift_speed":0.04284,"release.release_time":0.22197},"optimized_scores":{"best_composite_score":0.08107,"best_fitness_score":0.73107,"best_task_score":0.53795},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":754.0,"contact_point_centroid":[0.59136,0.1868,-0.00356],"force_p95":0.7162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35182,"mean_force":0.18164,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59141,0.17281,0.17577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":439.0,"contact_point_centroid":[0.59501,0.15063,0.22649],"force_p95":0.22403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41591,"mean_force":0.13159,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59399,0.16895,0.23164]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.52745,0.02837,-0.00157],"force_p95":0.3674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39933,"mean_force":0.12602,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5152,0.02854,0.04665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":687.0,"contact_point_centroid":[0.59518,0.1864,0.22263],"force_p95":0.16906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28087,"mean_force":0.09228,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59406,0.16928,0.22733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9204.0,"contact_point_centroid":[0.51938,0.04774,0.10339],"force_p95":0.08243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26675,"mean_force":0.0531,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5188,0.02866,0.10144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8196.0,"contact_point_centroid":[0.5192,0.00949,0.10518],"force_p95":0.08362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23995,"mean_force":0.05739,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51901,0.02867,0.10352]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53058,0.03065,-0.00218],"force_p95":0.17288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23206,"mean_force":0.13588,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51734,0.02869,0.04676]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7092.0,"contact_point_centroid":[0.55551,0.0711,0.19624],"force_p95":0.13266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21526,"mean_force":0.07139,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55418,0.09001,0.1969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8310.0,"contact_point_centroid":[0.55686,0.11171,0.19853],"force_p95":0.10608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18669,"mean_force":0.06065,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55572,0.09309,0.19871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4321.0,"contact_point_centroid":[0.51688,0.00939,0.04719],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14404,"mean_force":0.0496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51617,0.02861,0.04543]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.5305,0.03079,-0.00173],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12369,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50949,0.00981,0.2584]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52136,0.02505,0.13322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5194.0,"contact_point_centroid":[0.51727,0.04782,0.0476],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07758,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51618,0.02861,0.04544]}],"total_contact_groups":13},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59132,0.18678,0.01602],"final_tcp_position":[0.59623,0.17426,0.17614],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.35182,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12249,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51977,0.02107,0.21193],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.52483,0.02913,0.05573],"tcp_start":[0.51977,0.02107,0.21193],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.02928,0.02535],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16852,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11315.0,"raw_peak_contact_force":0.23206,"subtask_id":"grasp_object","tcp_end":[0.51615,0.02861,0.0454],"tcp_start":[0.52483,0.02913,0.05573],"tcp_to_object_dist_end":0.02466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.53455,0.02951,0.14015],"object_pos_start":[0.5305,0.02928,0.02535],"object_to_goal_dist_end":0.16654,"object_to_goal_dist_start":0.18489,"object_z_max":0.1399,"peak_contact_force":0.08116,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17499.0,"raw_peak_contact_force":0.39933,"subtask_id":"lift_object","tcp_end":[0.52541,0.02896,0.16389],"tcp_start":[0.51615,0.02861,0.0454],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.5972,0.16805,0.20905],"object_pos_start":[0.53455,0.02951,0.14015],"object_to_goal_dist_end":0.10161,"object_to_goal_dist_start":0.16654,"object_z_max":0.20895,"peak_contact_force":0.15018,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15402.0,"raw_peak_contact_force":0.21526,"subtask_id":"reach_goal","tcp_end":[0.59364,0.16741,0.24367],"tcp_start":[0.52541,0.02896,0.16389],"tcp_to_object_dist_end":0.0348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.59221,0.1829,0.05575],"object_pos_start":[0.5972,0.16805,0.20905],"object_to_goal_dist_end":0.05334,"object_to_goal_dist_start":0.10161,"object_z_max":0.20907,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1126.0,"raw_peak_contact_force":0.41591,"subtask_id":"place_goal","tcp_end":[0.59623,0.17426,0.17614],"tcp_start":[0.59364,0.16741,0.24367],"tcp_to_object_dist_end":0.12076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59132,0.18678,0.01602],"object_pos_start":[0.59221,0.1829,0.05575],"object_to_goal_dist_end":0.093,"object_to_goal_dist_start":0.05334,"object_z_max":0.05575,"peak_contact_force":0.1226,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":754.0,"raw_peak_contact_force":1.35182,"subtask_id":"place_goal","tcp_end":[0.59014,0.17235,0.19547],"tcp_start":[0.59623,0.17426,0.17614],"tcp_to_object_dist_end":0.18003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80405,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.39953,"approach_object.approach_speed":0.18665,"approach_object.approach_tolerance":0.03619,"descend_to_goal.descend_goal_speed":0.16416,"descend_to_goal.place_height":0.02337,"descend_to_object.descend_speed":0.10682,"descend_to_object.grasp_height":0.01189,"lift.lift_height":0.1749,"lift.lift_speed":0.05998,"release.release_time":0.42541},"optimized_scores":{"best_composite_score":-0.0832,"best_fitness_score":0.5668,"best_task_score":0.21109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":599.0,"contact_point_centroid":[0.58293,0.16406,-0.00443],"force_p95":0.97861,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9686,"mean_force":0.21787,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57367,0.15867,0.36033]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50176,-0.01432,-0.00142],"force_p95":0.3366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39348,"mean_force":0.09586,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49041,-0.01479,0.04897]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8552.0,"contact_point_centroid":[0.49384,0.0043,0.11434],"force_p95":0.08287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27089,"mean_force":0.05889,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49349,-0.01486,0.11329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5445.0,"contact_point_centroid":[0.52258,0.05574,0.23119],"force_p95":0.13052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26942,"mean_force":0.07739,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51981,0.03705,0.23226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9576.0,"contact_point_centroid":[0.49369,-0.03393,0.11392],"force_p95":0.08109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26427,"mean_force":0.05379,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49347,-0.01485,0.11294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5692.0,"contact_point_centroid":[0.52149,0.01587,0.22875],"force_p95":0.13079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24963,"mean_force":0.07342,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51869,0.03447,0.22958]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01561,-0.00208],"force_p95":0.14522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1935,"mean_force":0.12852,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49247,-0.01482,0.04894]},{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.50382,-0.01567,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12384,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5009,-0.00475,0.26065]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4348.0,"contact_point_centroid":[0.49173,0.00446,0.04899],"force_p95":0.07443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1241,"mean_force":0.0498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49135,-0.0148,0.04773]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.58291,0.16395,-0.00199],"force_p95":0.12272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12305,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58337,0.18135,0.33778]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49962,-0.01261,0.13559]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58291,0.16395,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58169,0.18356,0.29051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5417.0,"contact_point_centroid":[0.49096,-0.03393,0.0495],"force_p95":0.06562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06778,"mean_force":0.04061,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49136,-0.0148,0.04774]},{"body_a":"left_finger","body_b":"right_finger","contact_count":522.0,"contact_point_centroid":[0.57544,0.16208,0.36619],"force_p95":0.01372,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01118,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57521,0.16207,0.36394]},{"body_a":"left_finger","body_b":"right_finger","contact_count":671.0,"contact_point_centroid":[0.58374,0.18137,0.33986],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58337,0.18136,0.33765]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.58348,0.18424,0.28873],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58318,0.18422,0.28626]}],"total_contact_groups":16},"final_pose_error":0.01948,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58291,0.16395,0.01602],"final_tcp_position":[0.5844,0.18458,0.29058],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.90931,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.1223,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50147,-0.01036,0.21532],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.49969,-0.01488,0.05706],"tcp_start":[0.50147,-0.01036,0.21532],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01504,0.02571],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14391,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11565.0,"raw_peak_contact_force":0.1935,"subtask_id":"grasp_object","tcp_end":[0.49133,-0.0148,0.0477],"tcp_start":[0.49969,-0.01488,0.05706],"tcp_to_object_dist_end":0.02526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,-0.01516,0.15537],"object_pos_start":[0.50376,-0.01504,0.02571],"object_to_goal_dist_end":0.23674,"object_to_goal_dist_start":0.31206,"object_z_max":0.15511,"peak_contact_force":0.07741,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18213.0,"raw_peak_contact_force":0.39348,"subtask_id":"lift_object","tcp_end":[0.49919,-0.01496,0.18129],"tcp_start":[0.49133,-0.0148,0.0477],"tcp_to_object_dist_end":0.02706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.58291,0.16396,0.01599],"object_pos_start":[0.50696,-0.01516,0.15537],"object_to_goal_dist_end":0.23334,"object_to_goal_dist_start":0.23674,"object_z_max":0.26895,"peak_contact_force":0.12308,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12258.0,"raw_peak_contact_force":1.9686,"subtask_id":"reach_goal","tcp_end":[0.58239,0.17833,0.38101],"tcp_start":[0.49919,-0.01496,0.18129],"tcp_to_object_dist_end":0.36529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.58291,0.16395,0.01602],"object_pos_start":[0.58291,0.16396,0.01599],"object_to_goal_dist_end":0.23332,"object_to_goal_dist_start":0.23334,"object_z_max":0.01602,"peak_contact_force":273005.90931,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1303.0,"raw_peak_contact_force":0.12305,"subtask_id":"place_goal","tcp_end":[0.5844,0.18458,0.29058],"tcp_start":[0.58239,0.17833,0.38101],"tcp_to_object_dist_end":0.27534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58291,0.16395,0.01602],"object_pos_start":[0.58291,0.16395,0.01602],"object_to_goal_dist_end":0.23332,"object_to_goal_dist_start":0.23332,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58089,0.18317,0.31032],"tcp_start":[0.5844,0.18458,0.29058],"tcp_to_object_dist_end":0.29493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```