## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0765 | 0.40 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0041 | 0.37 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0090 | 0.27 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1377 | 0.35 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.33 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.076) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.4
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: impedance_control
  termination: time_limit
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
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.015
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
    - 0.08
    tolerance: 0.03
    orientation:
      mode: none
  parameters:
    transport_offset_z:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: place_contact
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: place_at_goal
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
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.015]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=none
  - parameter_bindings:
    - transport_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=place_contact, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.076
- **task_score** (E): 0.399
- **fitness_score**: 0.674  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1300 |
| descend | 1.00 | 1.00 | 0.1299 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 0.67 | 1.00 | 0.1022 |
| transport_to_goal | 1.00 | 0.67 | 0.1894 |
| descend_to_place | 1.00 | 1.00 | 0.0257 |
| release | 1.00 | 1.00 | 0.0216 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.175) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.016, 0.175)→(0.511, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.140 | 0.194 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.045)→(0.503, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 31.000 | 0.092 | 0.511 |
| lift | lift | 0.67 / step_budget | (0.503, 0.018, 0.036)→(0.509, 0.018, 0.138) | (0.516, 0.018, 0.026)→(0.519, 0.018, 0.119) | 0.237→0.199 | 1.00 / 29.000 | 0.112 | 0.228 |
| transport_to_goal | approach | 1.00 / step_budget | (0.509, 0.018, 0.138)→(0.592, 0.160, 0.215) | (0.519, 0.018, 0.119)→(0.599, 0.163, 0.193) | 0.199→0.034 | 0.67 / 22.000 | 0.059 | 0.379 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.163, 0.211)→(0.596, 0.169, 0.188) | (0.599, 0.163, 0.193)→(0.607, 0.171, 0.163) | 0.034→0.015 | 1.00 / 3.333 | 0.139 | 1.586 |
| release | release | 1.00 / step_budget | (0.596, 0.169, 0.188)→(0.591, 0.168, 0.208) | (0.609, 0.173, 0.152)→(0.609, 0.176, 0.020) | 0.025→0.149 | 1.00 / 4.000 | 7.060 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.466
- phase_breakdown.approach_object_score: 0.415
- phase_breakdown.place_at_goal_score: 0.307
- phase_breakdown.grasp_object_score: 0.570
- phase_breakdown.lift_object_score: 0.728
- grasp_place_fitness: 0.744

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.744
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: -0.051
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32864,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.13678,"approach_object.approach_speed":0.03266,"descend.descend_offset_z":0.02243,"descend.descend_speed":0.0727,"descend_to_place.place_offset_z":0.03174,"descend_to_place.place_speed":0.04244,"descend_to_place.place_tolerance":0.02093,"lift.lift_offset_z":0.16206,"lift.lift_speed":0.06747,"transport_to_goal.transport_offset_z":0.04638,"transport_to_goal.transport_speed":0.11356,"transport_to_goal.transport_tolerance":0.0342},"optimized_scores":{"best_composite_score":-0.00555,"best_fitness_score":0.74445,"best_task_score":0.5402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.59715,0.16092,-0.00835],"force_p95":1.3597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42116,"mean_force":0.56018,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58331,0.16129,0.15146]},{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.52771,0.02925,-0.00119],"force_p95":0.31183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53631,"mean_force":0.07449,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51572,0.02974,0.03683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":865.0,"contact_point_centroid":[0.59483,0.1446,0.13592],"force_p95":0.12359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50849,"mean_force":0.07281,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58719,0.16256,0.13609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":841.0,"contact_point_centroid":[0.58907,0.18175,0.13892],"force_p95":0.10344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50714,"mean_force":0.06983,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5874,0.16263,0.13639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":426.0,"contact_point_centroid":[0.59443,0.14012,0.14375],"force_p95":0.11761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47908,"mean_force":0.08543,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5872,0.15805,0.14326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":467.0,"contact_point_centroid":[0.58824,0.17698,0.14574],"force_p95":0.11143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39369,"mean_force":0.07973,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58718,0.15801,0.14329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16888.0,"contact_point_centroid":[0.5198,0.01067,0.08828],"force_p95":0.08965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30683,"mean_force":0.06006,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5178,0.02958,0.08667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16587.0,"contact_point_centroid":[0.51957,0.04858,0.08594],"force_p95":0.0966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30416,"mean_force":0.06162,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51763,0.02958,0.08435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3223.0,"contact_point_centroid":[0.56051,0.07401,0.14395],"force_p95":0.13552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26116,"mean_force":0.0838,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55382,0.09207,0.14298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3095.0,"contact_point_centroid":[0.5585,0.11415,0.14513],"force_p95":0.13261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22267,"mean_force":0.08409,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55545,0.09527,0.14308]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.0306,-0.00208],"force_p95":0.14719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21254,"mean_force":0.12928,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51853,0.02994,0.03669]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5106,0.01349,0.23638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.51787,0.01066,0.03808],"force_p95":0.07882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13623,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51731,0.02986,0.0353]},{"body_a":"world","body_b":"grasp_target","contact_count":3976.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52359,0.02929,0.0925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4946.0,"contact_point_centroid":[0.51788,0.04898,0.03711],"force_p95":0.07136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08043,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51731,0.02986,0.0353]}],"total_contact_groups":15},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60472,0.1592,0.01783],"final_tcp_position":[0.58965,0.16266,0.14017],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.42116,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3976.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52394,0.02768,0.17338],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1423,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10837.0,"raw_peak_contact_force":0.21254,"subtask_id":"grasp_object","tcp_end":[0.52542,0.03041,0.0446],"tcp_start":[0.52394,0.02768,0.17338],"tcp_to_object_dist_end":0.01927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02989,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18427,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.09681,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":33657.0,"raw_peak_contact_force":0.53631,"subtask_id":"grasp_object","tcp_end":[0.51728,0.02986,0.03526],"tcp_start":[0.52542,0.03041,0.0446],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53461,0.02982,0.1248],"object_pos_start":[0.53041,0.02989,0.0257],"object_to_goal_dist_end":0.16397,"object_to_goal_dist_start":0.18427,"object_z_max":0.12472,"peak_contact_force":0.10398,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6318.0,"raw_peak_contact_force":0.26116,"subtask_id":"lift_object","tcp_end":[0.52303,0.02961,0.14394],"tcp_start":[0.51728,0.02986,0.03526],"tcp_to_object_dist_end":0.02238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.59542,0.1572,0.12425],"object_pos_start":[0.53461,0.02982,0.1248],"object_to_goal_dist_end":0.02749,"object_to_goal_dist_start":0.16397,"object_z_max":0.12481,"peak_contact_force":0.10673,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":893.0,"raw_peak_contact_force":0.47908,"subtask_id":"place_at_goal","tcp_end":[0.58629,0.15482,0.1454],"tcp_start":[0.52303,0.02961,0.14394],"tcp_to_object_dist_end":0.02316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":33.0,"n_steps_budget":1000.0,"object_pos_end":[0.60105,0.16585,0.119],"object_pos_start":[0.59542,0.1572,0.12425],"object_to_goal_dist_end":0.01677,"object_to_goal_dist_start":0.02749,"object_z_max":0.12425,"peak_contact_force":0.16298,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1834.0,"raw_peak_contact_force":1.42116,"subtask_id":"place_at_goal","tcp_end":[0.58965,0.16266,0.14017],"tcp_start":[0.58629,0.15482,0.1454],"tcp_to_object_dist_end":0.02426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60472,0.1592,0.01783],"object_pos_start":[0.60105,0.16585,0.119],"object_to_goal_dist_end":0.09237,"object_to_goal_dist_start":0.01677,"object_z_max":0.119,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.58321,0.16127,0.16141],"tcp_start":[0.58965,0.16266,0.14017],"tcp_to_object_dist_end":0.1452,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87888,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.13121,"approach_object.approach_speed":0.03839,"descend.descend_offset_z":0.0201,"descend.descend_speed":0.01012,"descend_to_place.place_offset_z":0.00707,"descend_to_place.place_speed":0.0434,"descend_to_place.place_tolerance":0.02385,"lift.lift_offset_z":0.12558,"lift.lift_speed":0.08376,"transport_to_goal.transport_offset_z":0.05392,"transport_to_goal.transport_speed":0.09719,"transport_to_goal.transport_tolerance":0.031},"optimized_scores":{"best_composite_score":-0.17311,"best_fitness_score":0.57689,"best_task_score":0.20977},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":568.0,"contact_point_centroid":[0.61368,0.20381,-0.00437],"force_p95":0.93257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05879,"mean_force":0.22445,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57591,0.17616,0.26846]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.50188,-0.01518,-0.00114],"force_p95":0.29014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46467,"mean_force":0.06114,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48965,-0.01539,0.03995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.58007,0.18955,0.27719],"force_p95":0.33642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35107,"mean_force":0.17036,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57729,0.1701,0.28045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11423.0,"contact_point_centroid":[0.49504,0.00363,0.0849],"force_p95":0.10558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30896,"mean_force":0.0685,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49237,-0.01529,0.08289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.58921,0.15832,0.27438],"force_p95":0.1279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30626,"mean_force":0.06258,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57786,0.1714,0.2781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12387.0,"contact_point_centroid":[0.495,-0.03409,0.08336],"force_p95":0.10039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27419,"mean_force":0.06403,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49226,-0.01529,0.08184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4228.0,"contact_point_centroid":[0.53702,0.08902,0.20309],"force_p95":0.1542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25006,"mean_force":0.10393,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53379,0.07007,0.20324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4602.0,"contact_point_centroid":[0.54197,0.05236,0.20198],"force_p95":0.13706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19513,"mean_force":0.09672,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53354,0.06947,0.20279]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01557,-0.00203],"force_p95":0.13269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15117,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49216,-0.01543,0.0396]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49884,-0.00675,0.23549]},{"body_a":"world","body_b":"grasp_target","contact_count":3412.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49769,-0.01476,0.10405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.49141,0.00386,0.04113],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11283,"mean_force":0.05212,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.491,-0.01542,0.03836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.49085,-0.03447,0.04095],"force_p95":0.0639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08811,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.491,-0.01542,0.03836]}],"total_contact_groups":13},"final_pose_error":0.01597,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.61394,0.20367,0.01599],"final_tcp_position":[0.57961,0.17721,0.26504],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":20.93388,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3412.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49979,-0.01398,0.17013],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13157,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11225.0,"raw_peak_contact_force":0.15117,"subtask_id":"grasp_object","tcp_end":[0.49888,-0.01552,0.04683],"tcp_start":[0.49979,-0.01398,0.17013],"tcp_to_object_dist_end":0.02139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01527,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.11058,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":23976.0,"raw_peak_contact_force":0.46467,"subtask_id":"grasp_object","tcp_end":[0.49097,-0.01542,0.03832],"tcp_start":[0.49888,-0.01552,0.04683],"tcp_to_object_dist_end":0.01782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":782.0,"n_steps_budget":870.0,"object_pos_end":[0.51186,-0.01522,0.11946],"object_pos_start":[0.50372,-0.01527,0.02588],"object_to_goal_dist_end":0.25151,"object_to_goal_dist_start":0.3121,"object_z_max":0.11937,"peak_contact_force":0.16578,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8830.0,"raw_peak_contact_force":0.25006,"subtask_id":"lift_object","tcp_end":[0.49906,-0.01521,0.14055],"tcp_start":[0.49097,-0.01542,0.03832],"tcp_to_object_dist_end":0.02467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.58587,0.17257,0.25521],"object_pos_start":[0.51186,-0.01522,0.11946],"object_to_goal_dist_end":0.01652,"object_to_goal_dist_start":0.25151,"object_z_max":0.25505,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":226.0,"raw_peak_contact_force":0.35107,"subtask_id":"place_at_goal","tcp_end":[0.57727,0.16928,0.28068],"tcp_start":[0.49906,-0.01521,0.14055],"tcp_to_object_dist_end":0.02708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.59482,0.17851,0.23274],"object_pos_start":[0.58587,0.17257,0.25521],"object_to_goal_dist_end":0.01947,"object_to_goal_dist_start":0.01652,"object_z_max":0.25525,"peak_contact_force":0.12358,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":568.0,"raw_peak_contact_force":2.05879,"subtask_id":"place_at_goal","tcp_end":[0.57961,0.17721,0.26504],"tcp_start":[0.57973,0.17565,0.26944],"tcp_to_object_dist_end":0.03572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61394,0.20367,0.01599],"object_pos_start":[0.60008,0.18292,0.19973],"object_to_goal_dist_end":0.23426,"object_to_goal_dist_start":0.05035,"object_z_max":0.19973,"peak_contact_force":20.93388,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.57558,0.17604,0.28659],"tcp_start":[0.57961,0.17721,0.26504],"tcp_to_object_dist_end":0.2747,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13043,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.14309,"approach_object.approach_speed":0.0322,"descend.descend_offset_z":0.02074,"descend.descend_speed":0.0428,"descend_to_place.place_offset_z":-0.00451,"descend_to_place.place_speed":0.04916,"descend_to_place.place_tolerance":0.01605,"lift.lift_offset_z":0.16476,"lift.lift_speed":0.05819,"transport_to_goal.transport_offset_z":0.09348,"transport_to_goal.transport_speed":0.14377,"transport_to_goal.transport_tolerance":0.02231},"optimized_scores":{"best_composite_score":-0.05072,"best_fitness_score":0.69928,"best_task_score":0.44734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":252.0,"contact_point_centroid":[0.60552,0.16477,-0.0054],"force_p95":1.12923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27907,"mean_force":0.28256,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61304,0.16523,0.16637]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.50882,0.03766,-0.0012],"force_p95":0.33997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53264,"mean_force":0.08244,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49809,0.03845,0.03601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2616.0,"contact_point_centroid":[0.61123,0.18045,0.19314],"force_p95":0.07172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30678,"mean_force":0.04954,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61474,0.16176,0.19014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19710.0,"contact_point_centroid":[0.50001,0.05737,0.08314],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30237,"mean_force":0.05163,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49967,0.03827,0.08131]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1315.0,"contact_point_centroid":[0.61345,0.18514,0.15528],"force_p95":0.07018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30214,"mean_force":0.04313,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61692,0.1664,0.15227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19325.0,"contact_point_centroid":[0.50022,0.01915,0.08542],"force_p95":0.07816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29656,"mean_force":0.05193,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49983,0.03827,0.08327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1277.0,"contact_point_centroid":[0.61992,0.14732,0.15251],"force_p95":0.07195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27966,"mean_force":0.04489,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61691,0.1664,0.15225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.0395,-0.0021],"force_p95":0.15207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21815,"mean_force":0.13035,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50087,0.03871,0.03558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.61776,0.14272,0.19095],"force_p95":0.07336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21254,"mean_force":0.05136,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61473,0.16174,0.19028]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7396.0,"contact_point_centroid":[0.55856,0.07884,0.17361],"force_p95":0.08042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17169,"mean_force":0.05042,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55683,0.09792,0.17249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7038.0,"contact_point_centroid":[0.55727,0.11916,0.17666],"force_p95":0.07824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16014,"mean_force":0.05158,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55891,0.10019,0.17423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.50013,0.01934,0.0371],"force_p95":0.08101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1431,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49969,0.03861,0.03429]},{"body_a":"world","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50264,0.01712,0.24029]},{"body_a":"world","body_b":"grasp_target","contact_count":3928.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50621,0.03751,0.10007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5442.0,"contact_point_centroid":[0.49945,0.05771,0.0369],"force_p95":0.06792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08116,"mean_force":0.04087,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49969,0.03861,0.03429]}],"total_contact_groups":15},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60756,0.16392,0.02634],"final_tcp_position":[0.61945,0.16696,0.15751],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.27907,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3928.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50765,0.03539,0.18042],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14703,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11323.0,"raw_peak_contact_force":0.21815,"subtask_id":"grasp_object","tcp_end":[0.50758,0.03926,0.04297],"tcp_start":[0.50765,0.03539,0.18042],"tcp_to_object_dist_end":0.01766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03863,0.02566],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21315,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.06902,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":39237.0,"raw_peak_contact_force":0.53264,"subtask_id":"grasp_object","tcp_end":[0.49966,0.03861,0.03425],"tcp_start":[0.50758,0.03926,0.04297],"tcp_to_object_dist_end":0.01539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51104,0.03828,0.11307],"object_pos_start":[0.51243,0.03863,0.02566],"object_to_goal_dist_end":0.18061,"object_to_goal_dist_start":0.21315,"object_z_max":0.11297,"peak_contact_force":0.06608,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14434.0,"raw_peak_contact_force":0.17169,"subtask_id":"lift_object","tcp_end":[0.50371,0.03829,0.12942],"tcp_start":[0.49966,0.03861,0.03425],"tcp_to_object_dist_end":0.01792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.61706,0.15886,0.2001],"object_pos_start":[0.51104,0.03828,0.11307],"object_to_goal_dist_end":0.05771,"object_to_goal_dist_start":0.18061,"object_z_max":0.19988,"peak_contact_force":0.06914,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5120.0,"raw_peak_contact_force":0.30678,"subtask_id":"place_at_goal","tcp_end":[0.61143,0.1571,0.21862],"tcp_start":[0.50371,0.03829,0.12942],"tcp_to_object_dist_end":0.01944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.6261,0.16931,0.13819],"object_pos_start":[0.61706,0.15886,0.2001],"object_to_goal_dist_end":0.00769,"object_to_goal_dist_start":0.05771,"object_z_max":0.20027,"peak_contact_force":0.13073,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2844.0,"raw_peak_contact_force":1.27907,"subtask_id":"place_at_goal","tcp_end":[0.61945,0.16696,0.15751],"tcp_start":[0.61143,0.1571,0.21862],"tcp_to_object_dist_end":0.02057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60756,0.16392,0.02634],"object_pos_start":[0.6261,0.16931,0.13819],"object_to_goal_dist_end":0.12067,"object_to_goal_dist_start":0.00769,"object_z_max":0.13819,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1740.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.61295,0.1652,0.17684],"tcp_start":[0.61945,0.16696,0.15751],"tcp_to_object_dist_end":0.1506,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```