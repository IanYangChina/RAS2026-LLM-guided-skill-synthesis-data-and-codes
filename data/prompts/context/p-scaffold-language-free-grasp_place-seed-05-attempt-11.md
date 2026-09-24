## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2132 | 0.73 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2588 | 0.82 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1245 | 0.45 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0115 | 0.38 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0152 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.815, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.213) — your mutation base

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
  weight: 0.2
- id: grasp_target
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place_goal
  weight: 0.2
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_target
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    - -0.01
- id: lift_1
  type: lift
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: lift_clear
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: grip_transport
    when: during_phase
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
  subtask_id: transport_goal
- id: place_descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.05
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grip_place
    when: during_phase
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
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=grip_transport, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.01], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grip_place, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]

## Design Metrics

- **Composite score**: 0.213
- **task_score** (E): 0.734
- **fitness_score**: 0.833  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1700 |
| descend_1 | 1.00 | 1.00 | 0.0832 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 0.33 | 1.00 | 0.0948 |
| transport_1 | 1.00 | 1.00 | 0.1949 |
| place_descend_1 | 1.00 | 1.00 | 0.0294 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.025, 0.135) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.025, 0.135)→(0.510, 0.019, 0.052) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.052)→(0.502, 0.019, 0.043) | (0.516, 0.018, 0.026)→(0.516, 0.019, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.198 | 0.224 |
| lift_1 | lift | 0.33 / step_budget | (0.502, 0.019, 0.043)→(0.507, 0.019, 0.137) | (0.516, 0.019, 0.026)→(0.513, 0.019, 0.113) | 0.236→0.201 | 1.00 / 36.667 | 0.079 | 0.463 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.019, 0.137)→(0.597, 0.170, 0.213) | (0.513, 0.019, 0.113)→(0.596, 0.155, 0.109) | 0.201→0.101 | 1.00 / 16.667 | 91004.230 | 0.794 |
| place_descend_1 | descend | 1.00 / step_budget | (0.597, 0.170, 0.213)→(0.600, 0.176, 0.200) | (0.596, 0.155, 0.109)→(0.597, 0.157, 0.087) | 0.101→0.085 | 1.00 / 16.667 | 0.126 | 0.206 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.674
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.623
- phase_breakdown.lift_clear_score: 0.397
- phase_breakdown.transport_goal_score: 0.747
- phase_breakdown.place_goal_score: 0.496
- phase_breakdown.grasp_target_score: 0.655
- phase_breakdown.reach_object_score: 0.821
- grasp_place_fitness: 0.968

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.346
- **K-run variance**: 0.0359
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72024,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.20048,"approach_1.speed":0.06337,"descend_1.depth":0.01299,"descend_1.speed":0.06705,"lift_1.lift_height":0.14611,"lift_1.speed":0.0605,"place_descend_1.place_z_offset":0.01619,"place_descend_1.speed":0.06986,"transport_1.speed":0.18003,"transport_1.transport_z":0.09681},"optimized_scores":{"best_composite_score":0.34606,"best_fitness_score":0.96606,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.52742,0.03102,-0.00113],"force_p95":0.28992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4857,"mean_force":0.11588,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51502,0.03098,0.04441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17533.0,"contact_point_centroid":[0.51957,0.01168,0.09216],"force_p95":0.08258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28168,"mean_force":0.05836,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51785,0.03072,0.09036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18476.0,"contact_point_centroid":[0.51995,0.04972,0.09206],"force_p95":0.08092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27909,"mean_force":0.05597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51785,0.03072,0.09018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.59961,0.19112,0.16176],"force_p95":0.16801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2453,"mean_force":0.12176,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5948,0.17301,0.1664]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03075,-0.00203],"force_p95":0.22607,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23022,"mean_force":0.16218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51767,0.0312,0.04412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8288.0,"contact_point_centroid":[0.56106,0.11533,0.1641],"force_p95":0.12114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21711,"mean_force":0.07812,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5554,0.0968,0.16376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.59953,0.15483,0.16311],"force_p95":0.1465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21275,"mean_force":0.10536,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59479,0.17297,0.16704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7654.0,"contact_point_centroid":[0.56001,0.07681,0.16367],"force_p95":0.1336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19826,"mean_force":0.0834,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55468,0.09547,0.1632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.51734,0.05018,0.04454],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13959,"mean_force":0.05423,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51648,0.03112,0.04277]},{"body_a":"world","body_b":"grasp_target","contact_count":2592.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50988,0.03871,0.22306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.5173,0.01191,0.04554],"force_p95":0.08587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12931,"mean_force":0.06105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51648,0.03112,0.04277]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52377,0.03435,0.09435]}],"total_contact_groups":12},"final_pose_error":0.01465,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59933,0.1755,0.10042],"final_tcp_position":[0.5959,0.17523,0.13737],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.4857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2592.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52455,0.03701,0.13478],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":804.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.5249,0.03174,0.05265],"tcp_start":[0.52455,0.03701,0.13478],"tcp_to_object_dist_end":0.02723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.03084,0.02587],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18343,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22243,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10790.0,"raw_peak_contact_force":0.23022,"tcp_end":[0.51645,0.03112,0.04274],"tcp_start":[0.5249,0.03174,0.05265],"tcp_to_object_dist_end":0.02189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53182,0.03075,0.11624],"object_pos_start":[0.5304,0.03084,0.02587],"object_to_goal_dist_end":0.16365,"object_to_goal_dist_start":0.18343,"object_z_max":0.11612,"peak_contact_force":0.09319,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36201.0,"raw_peak_contact_force":0.4857,"subtask_id":"lift_clear","tcp_end":[0.52347,0.03062,0.14111],"tcp_start":[0.51645,0.03112,0.04274],"tcp_to_object_dist_end":0.02624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.59927,0.17168,0.15898],"object_pos_start":[0.53182,0.03075,0.11624],"object_to_goal_dist_end":0.0514,"object_to_goal_dist_start":0.16365,"object_z_max":0.15894,"peak_contact_force":0.1309,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15942.0,"raw_peak_contact_force":0.21711,"subtask_id":"transport_goal","tcp_end":[0.59461,0.17106,0.19407],"tcp_start":[0.52347,0.03062,0.14111],"tcp_to_object_dist_end":0.0354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.59933,0.1755,0.10042],"object_pos_start":[0.59927,0.17168,0.15898],"object_to_goal_dist_end":0.00856,"object_to_goal_dist_start":0.0514,"object_z_max":0.15898,"peak_contact_force":0.12415,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2185.0,"raw_peak_contact_force":0.2453,"subtask_id":"place_goal","tcp_end":[0.5959,0.17523,0.13737],"tcp_start":[0.59461,0.17106,0.19407],"tcp_to_object_dist_end":0.03712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77032,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.29781,"approach_1.speed":0.04975,"descend_1.depth":0.01333,"descend_1.speed":0.01039,"lift_1.lift_height":0.1656,"lift_1.speed":0.05614,"place_descend_1.place_z_offset":0.04836,"place_descend_1.speed":0.0415,"transport_1.speed":0.15562,"transport_1.transport_z":0.03022},"optimized_scores":{"best_composite_score":-0.05473,"best_fitness_score":0.56527,"best_task_score":0.2011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1197.0,"contact_point_centroid":[0.5683,0.1268,-0.00289],"force_p95":0.44304,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95476,"mean_force":0.16415,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56551,0.14577,0.2424]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.50058,-0.01357,-0.00123],"force_p95":0.23523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41898,"mean_force":0.0713,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48905,-0.01416,0.04597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8237.0,"contact_point_centroid":[0.52134,0.06,0.17006],"force_p95":0.10324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28078,"mean_force":0.07087,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51734,0.04124,0.17015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20650.0,"contact_point_centroid":[0.4914,-0.03337,0.09071],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27253,"mean_force":0.04954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49086,-0.01428,0.08889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18538.0,"contact_point_centroid":[0.49173,0.00488,0.0908],"force_p95":0.07701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26494,"mean_force":0.0542,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49086,-0.01428,0.08886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8263.0,"contact_point_centroid":[0.52022,0.01997,0.16855],"force_p95":0.11124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22386,"mean_force":0.06987,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51621,0.03873,0.16844]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01555,-0.00212],"force_p95":0.15654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21752,"mean_force":0.13189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49173,-0.01419,0.0454]},{"body_a":"world","body_b":"grasp_target","contact_count":2316.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.00905,0.21614]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.498,-0.01128,0.096]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.56821,0.1269,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5799,0.17841,0.27068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4903.0,"contact_point_centroid":[0.49125,0.00501,0.04699],"force_p95":0.07015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10948,"mean_force":0.04406,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49059,-0.01417,0.04418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.49118,-0.03346,0.04603],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0749,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49059,-0.01417,0.04419]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1076.0,"contact_point_centroid":[0.56803,0.15028,0.2479],"force_p95":0.01247,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56762,0.15028,0.24553]},{"body_a":"left_finger","body_b":"right_finger","contact_count":817.0,"contact_point_centroid":[0.58028,0.17839,0.27294],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01043,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57988,0.17837,0.27061]}],"total_contact_groups":14},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56821,0.1269,0.01602],"final_tcp_position":[0.58299,0.18398,0.28248],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273012.45321,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2316.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49962,-0.00865,0.13543],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":908.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49868,-0.01423,0.05307],"tcp_start":[0.49962,-0.00865,0.13543],"tcp_to_object_dist_end":0.02757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50377,-0.01468,0.02555],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31194,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15195,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11695.0,"raw_peak_contact_force":0.21752,"tcp_end":[0.49056,-0.01417,0.04415],"tcp_start":[0.49868,-0.01423,0.05307],"tcp_to_object_dist_end":0.02282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50029,-0.01455,0.11053],"object_pos_start":[0.50377,-0.01468,0.02555],"object_to_goal_dist_end":0.2593,"object_to_goal_dist_start":0.31194,"object_z_max":0.11044,"peak_contact_force":0.07505,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39390.0,"raw_peak_contact_force":0.41898,"subtask_id":"lift_clear","tcp_end":[0.49522,-0.01444,0.13607],"tcp_start":[0.49056,-0.01417,0.04415],"tcp_to_object_dist_end":0.02604,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56821,0.1269,0.01602],"object_pos_start":[0.50029,-0.01455,0.11053],"object_to_goal_dist_end":0.24059,"object_to_goal_dist_start":0.2593,"object_z_max":0.18084,"peak_contact_force":273012.45321,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18773.0,"raw_peak_contact_force":1.95476,"subtask_id":"transport_goal","tcp_end":[0.5778,0.17211,0.26063],"tcp_start":[0.49522,-0.01444,0.13607],"tcp_to_object_dist_end":0.24894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.56821,0.1269,0.01602],"object_pos_start":[0.56821,0.1269,0.01602],"object_to_goal_dist_end":0.24059,"object_to_goal_dist_start":0.24059,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1581.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58299,0.18398,0.28248],"tcp_start":[0.5778,0.17211,0.26063],"tcp_to_object_dist_end":0.27291,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39286,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.17151,"approach_1.speed":0.06619,"descend_1.depth":0.01047,"descend_1.speed":0.05874,"lift_1.lift_height":0.19442,"lift_1.speed":0.05759,"place_descend_1.place_z_offset":0.02215,"place_descend_1.speed":0.05752,"transport_1.speed":0.20623,"transport_1.transport_z":0.05044},"optimized_scores":{"best_composite_score":0.34827,"best_fitness_score":0.96827,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.50875,0.04014,-0.00115],"force_p95":0.28213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4834,"mean_force":0.11611,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49751,0.03981,0.04284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19330.0,"contact_point_centroid":[0.49982,0.05876,0.092],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28978,"mean_force":0.0526,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49882,0.03965,0.08975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19001.0,"contact_point_centroid":[0.49983,0.02057,0.09049],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26183,"mean_force":0.05325,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49871,0.03965,0.08805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.61993,0.18559,0.17908],"force_p95":0.12064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24962,"mean_force":0.08161,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61937,0.16701,0.18251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":249.0,"contact_point_centroid":[0.62056,0.14836,0.17915],"force_p95":0.11758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22943,"mean_force":0.08978,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61936,0.16701,0.18253]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03981,-0.00203],"force_p95":0.22105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22464,"mean_force":0.16173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50022,0.04006,0.04251]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13567.0,"contact_point_centroid":[0.55944,0.12144,0.15782],"force_p95":0.08941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20999,"mean_force":0.05498,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55885,0.10254,0.15753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12263.0,"contact_point_centroid":[0.55894,0.08264,0.15793],"force_p95":0.10437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19778,"mean_force":0.06061,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55807,0.1017,0.1572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.49969,0.05918,0.04391],"force_p95":0.08708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16,"mean_force":0.06227,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49907,0.03996,0.04124]},{"body_a":"world","body_b":"grasp_target","contact_count":2636.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.12969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50202,0.04587,0.22668]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50656,0.04361,0.09346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49976,0.0209,0.04315],"force_p95":0.0757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10202,"mean_force":0.0524,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49907,0.03996,0.04125]}],"total_contact_groups":12},"final_pose_error":0.01473,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62271,0.16828,0.14599],"final_tcp_position":[0.62007,0.16765,0.17888],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.4834,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":660.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2636.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50773,0.0466,0.13516],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":856.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50731,0.0407,0.0505],"tcp_start":[0.50773,0.0466,0.13516],"tcp_to_object_dist_end":0.02505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.04008,0.02586],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21213,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.2183,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.22464,"tcp_end":[0.49904,0.03996,0.04121],"tcp_start":[0.50731,0.0407,0.0505],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50835,0.03956,0.1125],"object_pos_start":[0.51242,0.04008,0.02586],"object_to_goal_dist_end":0.18152,"object_to_goal_dist_start":0.21213,"object_z_max":0.11241,"peak_contact_force":0.06954,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38523.0,"raw_peak_contact_force":0.4834,"subtask_id":"lift_clear","tcp_end":[0.50234,0.0397,0.13499],"tcp_start":[0.49904,0.03996,0.04121],"tcp_to_object_dist_end":0.02328,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.62048,0.16706,0.15161],"object_pos_start":[0.50835,0.03956,0.1125],"object_to_goal_dist_end":0.01111,"object_to_goal_dist_start":0.18152,"object_z_max":0.15158,"peak_contact_force":0.10599,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25830.0,"raw_peak_contact_force":0.20999,"subtask_id":"transport_goal","tcp_end":[0.61929,0.16659,0.18459],"tcp_start":[0.50234,0.0397,0.13499],"tcp_to_object_dist_end":0.03301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.62271,0.16828,0.14599],"object_pos_start":[0.62048,0.16706,0.15161],"object_to_goal_dist_end":0.00652,"object_to_goal_dist_start":0.01111,"object_z_max":0.15161,"peak_contact_force":0.13251,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":529.0,"raw_peak_contact_force":0.24962,"subtask_id":"place_goal","tcp_end":[0.62007,0.16765,0.17888],"tcp_start":[0.61929,0.16659,0.18459],"tcp_to_object_dist_end":0.033,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```