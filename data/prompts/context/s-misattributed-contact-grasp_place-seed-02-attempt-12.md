## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1687 | 0.20 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0270 | 0.23 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1661 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1158 | 0.21 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1322 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=-0.169) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.3
- id: reach_place
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.7
phases:
- id: approach_object
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
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
  retries:
    max_attempts: 0
    strategy: repeat
- id: descend_grasp
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
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  retries:
    max_attempts: 0
    strategy: repeat
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
    orientation:
      mode: keep_current
  parameters:
    retry_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.z
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
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
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: add
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_place
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    place_descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
    place_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    orientation:
      mode: keep_current
  parameters:
    release_time:
      type: scalar
      range:
      - 1.0
      - 4.0
      default: 2.5
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract
  type: retract
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
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
  - retries: max_attempts=0, strategy=repeat
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (add)
  - retries: max_attempts=0, strategy=repeat
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retry_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_z: status=consumed; consumers=retry.offset.z (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (add)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - place_descend_z_offset: status=consumed; consumers=target.offset.z (add)
    - place_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.169
- **task_score** (E): 0.200
- **fitness_score**: 0.561  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0652 |
| descend_grasp | 1.00 | 1.00 | 0.1964 |
| grasp | 1.00 | 1.00 | 0.0113 |
| lift | 1.00 | 1.00 | 0.1006 |
| approach_goal | 0.00 | 1.00 | 0.2313 |
| descend_place | 1.00 | 1.00 | 0.2126 |
| release | 1.00 | 1.00 | 0.0197 |
| retract | 0.33 | 1.00 | 0.1598 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.012, 0.252) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.493, -0.012, 0.252)→(0.489, -0.015, 0.056) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 43.333 | 0.144 | 0.167 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.056)→(0.481, -0.015, 0.048) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 22.333 | 0.109 | 0.425 |
| lift | lift | 1.00 / step_budget | (0.481, -0.015, 0.048)→(0.477, -0.015, 0.148) | (0.493, -0.015, 0.026)→(0.488, -0.015, 0.119) | 0.281→0.250 | 1.00 / 8.000 | 0.123 | 1.619 |
| approach_goal | approach | 0.00 / step_budget | (0.529, 0.052, 0.230)→(0.632, 0.171, 0.395) | (0.488, -0.015, 0.119)→(0.523, 0.029, 0.016) | 0.250→0.243 | 1.00 / 8.667 | 182003.585 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.632, 0.171, 0.395)→(0.633, 0.174, 0.182) | (0.523, 0.029, 0.016)→(0.523, 0.029, 0.016) | 0.243→0.243 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.633, 0.174, 0.182)→(0.627, 0.172, 0.201) | (0.523, 0.029, 0.016)→(0.523, 0.029, 0.016) | 0.243→0.243 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 0.33 / step_budget | (0.627, 0.172, 0.201)→(0.625, 0.171, 0.361) | (0.523, 0.029, 0.016)→(0.523, 0.029, 0.016) | 0.243→0.243 | 1.00 / 4.000 | 8.829 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.229
- phase_score: 0.109
- phase_breakdown.reach_place_score: 0.156
- phase_breakdown.reach_grasp_score: 0.000
- grasp_place_fitness: 0.579

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.579
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.229
- **Median Q (composite search score)**: -0.175
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: approach_goal.approach_speed
- **Final σ (mean)**: 0.282


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11712,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16871,"approach_goal.approach_speed":0.09078,"approach_object.approach_height":0.10096,"descend_grasp.descend_offset_z":-0.00928,"descend_place.place_descend_z_offset":0.00225,"descend_place.place_tolerance":0.01166,"grasp.retry_x":0.00095,"grasp.retry_z":-0.00121,"lift.lift_height":0.10083,"release.release_time":2.61536,"retract.retract_height":0.13982},"optimized_scores":{"best_composite_score":-0.17994,"best_fitness_score":0.55006,"best_task_score":0.17698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5129.0,"contact_point_centroid":[0.5075,0.01139,-0.00218],"force_p95":0.12368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63009,"mean_force":0.13176,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54507,0.0718,0.30396]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.47366,-0.01897,-0.00112],"force_p95":0.30395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41788,"mean_force":0.05478,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46338,-0.01953,0.04989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9160.0,"contact_point_centroid":[0.46282,-0.00046,0.08874],"force_p95":0.10238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28819,"mean_force":0.06459,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46098,-0.01945,0.08834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10235.0,"contact_point_centroid":[0.46261,-0.03837,0.08888],"force_p95":0.09565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28576,"mean_force":0.05872,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46098,-0.01946,0.08844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6358.0,"contact_point_centroid":[0.47688,0.01343,0.16045],"force_p95":0.13233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24179,"mean_force":0.08579,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47115,-0.00514,0.16065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6755.0,"contact_point_centroid":[0.47687,-0.02338,0.16067],"force_p95":0.13073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19052,"mean_force":0.08,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47133,-0.00494,0.16101]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02014,-0.00205],"force_p95":0.13833,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17211,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46581,-0.01959,0.04923]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.47616,-0.02015,-0.00184],"force_p95":0.13755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48901,-0.00747,0.27066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.4642,-0.00036,0.04816],"force_p95":0.06858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12637,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46475,-0.01956,0.04814]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47401,-0.01783,0.14686]},{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.50751,0.01139,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62828,0.15644,0.33386]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50751,0.01139,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62408,0.15674,0.20283]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50751,0.01139,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62056,0.15557,0.30013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.46446,-0.03877,0.04893],"force_p95":0.06686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08543,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46475,-0.01956,0.04814]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5219.0,"contact_point_centroid":[0.54733,0.07416,0.31066],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54733,0.07415,0.30833]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2557.0,"contact_point_centroid":[0.62826,0.15645,0.33645],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62828,0.15644,0.3341]}],"total_contact_groups":17},"final_pose_error":0.07903,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50751,0.01139,0.01602],"final_tcp_position":[0.62151,0.15575,0.3831],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273005.56723,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47812,-0.01601,0.23985],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13794,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11731.0,"raw_peak_contact_force":0.17211,"tcp_end":[0.4722,-0.01974,0.05584],"tcp_start":[0.47812,-0.01601,0.23985],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01976,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.10285,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19524.0,"raw_peak_contact_force":0.41788,"tcp_end":[0.46472,-0.01956,0.04811],"tcp_start":[0.4722,-0.01974,0.05584],"tcp_to_object_dist_end":0.02504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.47197,-0.01969,0.11007],"object_pos_start":[0.47609,-0.01976,0.0258],"object_to_goal_dist_end":0.25261,"object_to_goal_dist_start":0.2883,"object_z_max":0.10996,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23461.0,"raw_peak_contact_force":1.63009,"tcp_end":[0.46094,-0.01944,0.13785],"tcp_start":[0.46472,-0.01956,0.04811],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.50751,0.01139,0.01602],"object_pos_start":[0.47197,-0.01969,0.11007],"object_to_goal_dist_end":0.25975,"object_to_goal_dist_start":0.25261,"object_z_max":0.15501,"peak_contact_force":273005.56723,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4945.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.62788,0.15507,0.46223],"tcp_start":[0.5028,0.02776,0.22263],"tcp_to_object_dist_end":0.48397,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.50751,0.01139,0.01602],"object_pos_start":[0.50751,0.01139,0.01602],"object_to_goal_dist_end":0.25975,"object_to_goal_dist_start":0.25975,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62814,0.15796,0.20324],"tcp_start":[0.62788,0.15507,0.46223],"tcp_to_object_dist_end":0.26662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50751,0.01139,0.01602],"object_pos_start":[0.50751,0.01139,0.01602],"object_to_goal_dist_end":0.25975,"object_to_goal_dist_start":0.25975,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62269,0.15629,0.22231],"tcp_start":[0.62814,0.15796,0.20324],"tcp_to_object_dist_end":0.27715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50751,0.01139,0.01602],"object_pos_start":[0.50751,0.01139,0.01602],"object_to_goal_dist_end":0.25975,"object_to_goal_dist_start":0.25975,"object_z_max":0.01602,"peak_contact_force":26.2408,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":784.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62151,0.15575,0.3831],"tcp_start":[0.62269,0.15629,0.22231],"tcp_to_object_dist_end":0.41059,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9633,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11724,"approach_goal.approach_speed":0.14009,"approach_object.approach_height":0.17188,"descend_grasp.descend_offset_z":-0.00743,"descend_place.place_descend_z_offset":0.01393,"descend_place.place_tolerance":0.01116,"grasp.retry_x":-0.00244,"grasp.retry_z":-0.00076,"lift.lift_height":0.11761,"release.release_time":2.10193,"retract.retract_height":0.10776},"optimized_scores":{"best_composite_score":-0.17506,"best_fitness_score":0.55494,"best_task_score":0.19315},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6198.0,"contact_point_centroid":[0.49283,0.02831,-0.00213],"force_p95":0.12326,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52606,"mean_force":0.13011,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53593,0.09406,0.24888]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.45628,-0.02386,-0.00124],"force_p95":0.27082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41259,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44633,-0.02552,0.05255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6821.0,"contact_point_centroid":[0.44686,-0.00686,0.09334],"force_p95":0.13396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33919,"mean_force":0.09347,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4442,-0.02542,0.09562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8766.0,"contact_point_centroid":[0.44564,-0.04373,0.09133],"force_p95":0.12837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27821,"mean_force":0.07553,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44415,-0.02542,0.09269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2466.0,"contact_point_centroid":[0.45879,-0.02854,0.16241],"force_p95":0.15201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21253,"mean_force":0.10597,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45303,-0.01037,0.16574]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02639,-0.00211],"force_p95":0.15909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18289,"mean_force":0.13123,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44875,-0.02562,0.05152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2638.0,"contact_point_centroid":[0.46025,0.0089,0.16367],"force_p95":0.13,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17625,"mean_force":0.09799,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45389,-0.00921,0.1666]},{"body_a":"world","body_b":"grasp_target","contact_count":712.0,"contact_point_centroid":[0.45856,-0.02632,-0.00182],"force_p95":0.1376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12331,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.482,-0.01011,0.29727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4556.0,"contact_point_centroid":[0.44818,-0.00633,0.05092],"force_p95":0.09524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13707,"mean_force":0.05147,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44773,-0.02558,0.05051]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45894,-0.02321,0.17584]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.49286,0.02831,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62471,0.20422,0.23866]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49286,0.02831,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6209,0.20448,0.13727]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49286,0.02831,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61631,0.20267,0.23347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4906.0,"contact_point_centroid":[0.44776,-0.04444,0.05085],"force_p95":0.07012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08258,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44773,-0.02558,0.05052]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6282.0,"contact_point_centroid":[0.53902,0.09789,0.25418],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01057,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53898,0.09788,0.25192]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2021.0,"contact_point_centroid":[0.62483,0.20422,0.24132],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62471,0.20422,0.23896]}],"total_contact_groups":17},"final_pose_error":0.04893,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.49286,0.02831,0.01602],"final_tcp_position":[0.61713,0.20288,0.31556],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.52606,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46492,-0.02068,0.29664],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16318,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11262.0,"raw_peak_contact_force":0.18289,"tcp_end":[0.45493,-0.02585,0.05768],"tcp_start":[0.46492,-0.02068,0.29664],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02573,0.02539],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3034,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13682,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15722.0,"raw_peak_contact_force":0.41259,"tcp_end":[0.4477,-0.02557,0.05049],"tcp_start":[0.45493,-0.02585,0.05768],"tcp_to_object_dist_end":0.02733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45069,-0.02566,0.12311],"object_pos_start":[0.45851,-0.02573,0.02539],"object_to_goal_dist_end":0.29491,"object_to_goal_dist_start":0.3034,"object_z_max":0.123,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17584.0,"raw_peak_contact_force":1.52606,"tcp_end":[0.44412,-0.0254,0.1571],"tcp_start":[0.4477,-0.02557,0.05049],"tcp_to_object_dist_end":0.03462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1923.0,"n_steps_budget":1000.0,"object_pos_end":[0.49286,0.02831,0.01602],"object_pos_start":[0.45069,-0.02566,0.12311],"object_to_goal_dist_end":0.24664,"object_to_goal_dist_start":0.29491,"object_z_max":0.13968,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3929.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.62459,0.20274,0.33831],"tcp_start":[0.51139,0.06286,0.22498],"tcp_to_object_dist_end":0.38942,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.49286,0.02831,0.01602],"object_pos_start":[0.49286,0.02831,0.01602],"object_to_goal_dist_end":0.24664,"object_to_goal_dist_start":0.24664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62579,0.20628,0.13791],"tcp_start":[0.62459,0.20274,0.33831],"tcp_to_object_dist_end":0.25338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49286,0.02831,0.01602],"object_pos_start":[0.49286,0.02831,0.01602],"object_to_goal_dist_end":0.24664,"object_to_goal_dist_start":0.24664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61917,0.2038,0.15667],"tcp_start":[0.62579,0.20628,0.13791],"tcp_to_object_dist_end":0.25794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49286,0.02831,0.01602],"object_pos_start":[0.49286,0.02831,0.01602],"object_to_goal_dist_end":0.24664,"object_to_goal_dist_start":0.24664,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":712.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61713,0.20288,0.31556],"tcp_start":[0.61917,0.2038,0.15667],"tcp_to_object_dist_end":0.36829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08122,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.08708,"approach_goal.approach_speed":0.15,"approach_object.approach_height":0.08553,"descend_grasp.descend_offset_z":-0.00999,"descend_place.place_descend_z_offset":0.00372,"descend_place.place_tolerance":0.01174,"grasp.retry_x":0.00097,"grasp.retry_z":-0.00279,"lift.lift_height":0.11787,"release.release_time":2.70574,"retract.retract_height":0.1388},"optimized_scores":{"best_composite_score":-0.15103,"best_fitness_score":0.57897,"best_task_score":0.22852},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5338.0,"contact_point_centroid":[0.56832,0.04815,-0.00218],"force_p95":0.12353,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70181,"mean_force":0.13098,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59298,0.09094,0.2831]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54177,0.00098,-0.00111],"force_p95":0.3185,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44407,"mean_force":0.06522,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52914,0.00086,0.04597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10767.0,"contact_point_centroid":[0.52974,0.01971,0.09566],"force_p95":0.09303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32858,"mean_force":0.06388,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52654,0.00083,0.09324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10455.0,"contact_point_centroid":[0.52961,-0.01806,0.09287],"force_p95":0.09713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28775,"mean_force":0.06552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52658,0.00083,0.09078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5750.0,"contact_point_centroid":[0.54095,0.03448,0.16947],"force_p95":0.12912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26992,"mean_force":0.07853,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53512,0.01604,0.16843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.5402,-0.00329,0.16844],"force_p95":0.15651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26122,"mean_force":0.08821,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53462,0.01535,0.1674]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00104,-0.00203],"force_p95":0.13121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14727,"mean_force":0.12525,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53193,0.00092,0.04573]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51656,0.00046,0.25931]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.536,0.00098,0.13644]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.56833,0.04816,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.64407,0.15555,0.29589]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56833,0.04816,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64022,0.15562,0.2049]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56833,0.04816,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63676,0.15449,0.30124]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4217.0,"contact_point_centroid":[0.53132,-0.01829,0.04694],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10317,"mean_force":0.05085,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53074,0.0009,0.04432]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4776.0,"contact_point_centroid":[0.53134,0.01998,0.04631],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09306,"mean_force":0.04541,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53075,0.0009,0.04432]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5433.0,"contact_point_centroid":[0.59476,0.09316,0.28881],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01571,"mean_force":0.01054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5947,0.09316,0.2865]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.64257,0.15636,0.20393],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64259,0.15634,0.20152]}],"total_contact_groups":17},"final_pose_error":0.07911,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56833,0.04816,0.01602],"final_tcp_position":[0.63775,0.15468,0.38386],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273005.06534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53549,0.00095,0.2202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14727,"tcp_end":[0.53903,0.00104,0.0543],"tcp_start":[0.53549,0.00095,0.2202],"tcp_to_object_dist_end":0.02877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00094,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25038,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.08681,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21364.0,"raw_peak_contact_force":0.44407,"tcp_end":[0.53072,0.00089,0.04428],"tcp_start":[0.53903,0.00104,0.0543],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53986,0.00094,0.12517],"object_pos_start":[0.54421,0.00094,0.02588],"object_to_goal_dist_end":0.20163,"object_to_goal_dist_start":0.25038,"object_z_max":0.12506,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21590.0,"raw_peak_contact_force":1.70181,"tcp_end":[0.52673,0.00084,0.1496],"tcp_start":[0.53072,0.00089,0.04428],"tcp_to_object_dist_end":0.02773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1908.0,"n_steps_budget":1000.0,"object_pos_end":[0.56833,0.04816,0.01602],"object_pos_start":[0.53986,0.00094,0.12517],"object_to_goal_dist_end":0.22142,"object_to_goal_dist_start":0.20163,"object_z_max":0.16306,"peak_contact_force":273005.06534,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3327.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.6442,0.15459,0.38403],"tcp_start":[0.57246,0.06397,0.24295],"tcp_to_object_dist_end":0.39053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.56833,0.04816,0.01602],"object_pos_start":[0.56833,0.04816,0.01602],"object_to_goal_dist_end":0.22142,"object_to_goal_dist_start":0.22142,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64428,0.15681,0.20582],"tcp_start":[0.6442,0.15459,0.38403],"tcp_to_object_dist_end":0.23151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56833,0.04816,0.01602],"object_pos_start":[0.56833,0.04816,0.01602],"object_to_goal_dist_end":0.22142,"object_to_goal_dist_start":0.22142,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63884,0.15518,0.22416],"tcp_start":[0.64428,0.15681,0.20582],"tcp_to_object_dist_end":0.24444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56833,0.04816,0.01602],"object_pos_start":[0.56833,0.04816,0.01602],"object_to_goal_dist_end":0.22142,"object_to_goal_dist_start":0.22142,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63775,0.15468,0.38386],"tcp_start":[0.63884,0.15518,0.22416],"tcp_to_object_dist_end":0.38919,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```