## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0270 | 0.23 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1661 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1158 | 0.21 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1322 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0222 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.027) — your mutation base

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

- **Composite score**: -0.027
- **task_score** (E): 0.232
- **fitness_score**: 0.578  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0535 |
| descend_grasp | 1.00 | 1.00 | 0.2067 |
| grasp | 1.00 | 1.00 | 0.0113 |
| lift | 1.00 | 0.67 | 0.1156 |
| approach_goal | 0.00 | 1.00 | 0.0238 |
| descend_place | 1.00 | 1.00 | 0.0025 |
| release | 1.00 | 1.00 | 0.0252 |
| retract | 0.33 | 1.00 | 0.1619 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.012, 0.262) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.493, -0.012, 0.262)→(0.489, -0.015, 0.056) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 41.333 | 0.136 | 0.168 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.056)→(0.481, -0.015, 0.047) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 23.667 | 0.105 | 0.415 |
| lift | lift | 1.00 / step_budget | (0.481, -0.015, 0.047)→(0.477, -0.015, 0.163) | (0.493, -0.015, 0.026)→(0.488, -0.015, 0.134) | 0.281→0.246 | 0.67 / 4.000 | 0.005 | 0.271 |
| approach_goal | approach | 0.00 / guard_failure | (0.498, 0.014, 0.184)→(0.508, 0.027, 0.201) | (0.488, -0.015, 0.134)→(0.507, 0.014, 0.151) | 0.246→0.209 | 1.00 / 3.333 | 3257.221 | 0.114 |
| descend_place | descend | 1.00 / force_exceeded | (0.508, 0.027, 0.201)→(0.508, 0.029, 0.199) | (0.517, 0.029, 0.164)→(0.521, 0.035, 0.129) | 0.190→0.187 | 1.00 / 3.333 | 0.158 | 1.745 |
| release | release | 1.00 / step_budget | (0.508, 0.029, 0.199)→(0.503, 0.029, 0.224) | (0.521, 0.035, 0.129)→(0.536, 0.058, 0.018) | 0.187→0.220 | 1.00 / 4.000 | 2.403 | 0.202 |
| retract | retract | 0.33 / step_budget | (0.503, 0.029, 0.224)→(0.502, 0.029, 0.386) | (0.536, 0.058, 0.018)→(0.536, 0.061, 0.016) | 0.220→0.220 | 1.00 / 4.000 | 6.757 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.260
- phase_score: 0.033
- phase_breakdown.reach_place_score: 0.048
- phase_breakdown.reach_grasp_score: 0.000
- grasp_place_fitness: 0.595

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.595
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.260
- **Median Q (composite search score)**: -0.034
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92143,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.1033,"approach_goal.approach_speed":0.1587,"approach_object.approach_height":0.11334,"descend_grasp.descend_offset_z":-0.00925,"descend_place.place_descend_z_offset":-0.00366,"descend_place.place_force_threshold":5.90876,"grasp.retry_x":0.0001,"grasp.retry_z":0.00586,"lift.lift_height":0.12741,"release.release_time":2.53389,"retract.retract_height":0.11116},"optimized_scores":{"best_composite_score":-0.03648,"best_fitness_score":0.56852,"best_task_score":0.21358},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":219.0,"contact_point_centroid":[0.51333,0.0432,-0.00749],"force_p95":1.3637,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69039,"mean_force":0.42701,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.48394,0.01356,0.20626]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.47346,-0.01908,-0.00113],"force_p95":0.29751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41732,"mean_force":0.05423,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46343,-0.01951,0.04976]},{"body_a":"world","body_b":"grasp_target","contact_count":3958.0,"contact_point_centroid":[0.51431,0.06082,-0.00202],"force_p95":0.12471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35868,"mean_force":0.12473,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48134,0.01348,0.30198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.49514,0.0284,0.19019],"force_p95":0.27785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30232,"mean_force":0.18282,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.48806,0.0138,0.19548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10839.0,"contact_point_centroid":[0.46364,-0.00051,0.09989],"force_p95":0.10287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29152,"mean_force":0.06794,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46103,-0.01943,0.09954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11868.0,"contact_point_centroid":[0.46339,-0.03829,0.09912],"force_p95":0.09818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28853,"mean_force":0.06288,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46103,-0.01943,0.09869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4066.0,"contact_point_centroid":[0.47909,-0.02219,0.17739],"force_p95":0.12658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25622,"mean_force":0.0859,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47306,-0.00371,0.17822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4176.0,"contact_point_centroid":[0.47932,0.01503,0.1776],"force_p95":0.12885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22077,"mean_force":0.08509,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47324,-0.00349,0.17844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15.0,"contact_point_centroid":[0.49521,0.03068,0.19182],"force_p95":0.18472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19901,"mean_force":0.14005,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48859,0.01344,0.19653]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.49623,-0.00417,0.19071],"force_p95":0.17709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18025,"mean_force":0.118,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48859,0.01344,0.19653]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02012,-0.00205],"force_p95":0.13887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17281,"mean_force":0.12689,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46585,-0.01957,0.0491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11.0,"contact_point_centroid":[0.49682,-0.00301,0.19019],"force_p95":0.15114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15546,"mean_force":0.09596,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.48869,0.01368,0.19643]},{"body_a":"world","body_b":"grasp_target","contact_count":672.0,"contact_point_centroid":[0.47616,-0.02015,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48957,-0.00714,0.27642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4511.0,"contact_point_centroid":[0.46482,-0.00035,0.04846],"force_p95":0.07379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13409,"mean_force":0.04797,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46479,-0.01954,0.04801]},{"body_a":"world","body_b":"grasp_target","contact_count":2448.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47452,-0.01752,0.1525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.46484,-0.03869,0.04911],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0858,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46479,-0.01954,0.04802]}],"total_contact_groups":16},"final_pose_error":0.05022,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.51432,0.06104,0.01602],"final_tcp_position":[0.48195,0.01349,0.38275],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2448.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47904,-0.0154,0.25156],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1385,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11212.0,"raw_peak_contact_force":0.17281,"tcp_end":[0.47223,-0.01972,0.05571],"tcp_start":[0.47904,-0.0154,0.25156],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01975,0.02579],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.09751,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":22833.0,"raw_peak_contact_force":0.41732,"tcp_end":[0.46476,-0.01954,0.04799],"tcp_start":[0.47223,-0.01972,0.05571],"tcp_to_object_dist_end":0.02492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.47116,-0.01974,0.13483],"object_pos_start":[0.47609,-0.01975,0.02579],"object_to_goal_dist_end":0.24646,"object_to_goal_dist_start":0.2883,"object_z_max":0.13472,"peak_contact_force":0.01017,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8242.0,"raw_peak_contact_force":0.25622,"tcp_end":[0.46115,-0.01942,0.16408],"tcp_start":[0.46476,-0.01954,0.04799],"tcp_to_object_dist_end":0.03092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.49492,0.01192,0.16379],"object_pos_start":[0.47116,-0.01974,0.13483],"object_to_goal_dist_end":0.20251,"object_to_goal_dist_start":0.24646,"object_z_max":0.16381,"peak_contact_force":9760.30694,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27.0,"raw_peak_contact_force":0.19901,"subtask_id":"reach_place","tcp_end":[0.48854,0.01335,0.19652],"tcp_start":[0.48791,0.01223,0.19596],"tcp_to_object_dist_end":0.03338,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49648,0.01409,0.16296],"object_pos_start":[0.49606,0.01343,0.16353],"object_to_goal_dist_end":0.19999,"object_to_goal_dist_start":0.20067,"object_z_max":0.16353,"peak_contact_force":0.22768,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":348.0,"raw_peak_contact_force":1.69039,"tcp_end":[0.48872,0.01362,0.19649],"tcp_start":[0.48854,0.01335,0.19652],"tcp_to_object_dist_end":0.03442,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51403,0.05089,0.02057],"object_pos_start":[0.49648,0.01409,0.16296],"object_to_goal_dist_end":0.23285,"object_to_goal_dist_start":0.19999,"object_z_max":0.16296,"peak_contact_force":6.96311,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3958.0,"raw_peak_contact_force":0.35868,"tcp_end":[0.48374,0.01356,0.22177],"tcp_start":[0.48872,0.01362,0.19649],"tcp_to_object_dist_end":0.20687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51432,0.06104,0.01602],"object_pos_start":[0.51403,0.05089,0.02057],"object_to_goal_dist_end":0.23156,"object_to_goal_dist_start":0.23285,"object_z_max":0.02057,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":672.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48195,0.01349,0.38275],"tcp_start":[0.48374,0.01356,0.22177],"tcp_to_object_dist_end":0.37122,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84932,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11627,"approach_goal.approach_speed":0.15961,"approach_object.approach_height":0.15764,"descend_grasp.descend_offset_z":-0.00843,"descend_place.place_descend_z_offset":0.00017,"descend_place.place_force_threshold":4.39665,"grasp.retry_x":0.00221,"grasp.retry_z":0.00342,"lift.lift_height":0.116,"release.release_time":2.22559,"retract.retract_height":0.1379},"optimized_scores":{"best_composite_score":-0.03442,"best_fitness_score":0.57058,"best_task_score":0.22085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":750.0,"contact_point_centroid":[0.50472,0.04652,-0.00334],"force_p95":0.72156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55943,"mean_force":0.18825,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.47248,0.02254,0.17813]},{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.45608,-0.02498,-0.00114],"force_p95":0.30014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38285,"mean_force":0.0478,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44646,-0.02548,0.05126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8982.0,"contact_point_centroid":[0.44595,-0.00656,0.09212],"force_p95":0.12908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28824,"mean_force":0.07441,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44414,-0.02538,0.09289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10518.0,"contact_point_centroid":[0.44572,-0.04395,0.09338],"force_p95":0.12349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28391,"mean_force":0.06541,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44414,-0.02538,0.09372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3014.0,"contact_point_centroid":[0.46362,-0.02213,0.16188],"force_p95":0.1502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24504,"mean_force":0.10608,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45794,-0.00416,0.16472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2806.0,"contact_point_centroid":[0.46538,0.01605,0.16328],"force_p95":0.13832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21988,"mean_force":0.11228,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45957,-0.002,0.16601]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02625,-0.00206],"force_p95":0.14246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1842,"mean_force":0.12773,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44881,-0.02557,0.0505]},{"body_a":"world","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.45856,-0.02632,-0.0018],"force_p95":0.13769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1234,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48297,-0.00953,0.29225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.44865,-0.00632,0.05002],"force_p95":0.07807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13781,"mean_force":0.05217,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44778,-0.02553,0.04949]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50494,0.04689,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46872,0.02235,0.27951]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45945,-0.02287,0.17003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.44781,-0.0446,0.05014],"force_p95":0.06959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07778,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44778,-0.02553,0.0495]}],"total_contact_groups":12},"final_pose_error":0.07519,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.50494,0.04689,0.01602],"final_tcp_position":[0.46926,0.02237,0.36185],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":20.02587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.46592,-0.02004,0.28585],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14068,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10821.0,"raw_peak_contact_force":0.1842,"tcp_end":[0.45499,-0.0258,0.05665],"tcp_start":[0.46592,-0.02004,0.28585],"tcp_to_object_dist_end":0.03085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02573,0.02575],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13451,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19625.0,"raw_peak_contact_force":0.38285,"tcp_end":[0.44775,-0.02553,0.04947],"tcp_start":[0.45499,-0.0258,0.05665],"tcp_to_object_dist_end":0.02604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45209,-0.02594,0.1222],"object_pos_start":[0.4585,-0.02573,0.02575],"object_to_goal_dist_end":0.29427,"object_to_goal_dist_start":0.30331,"object_z_max":0.12209,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5820.0,"raw_peak_contact_force":0.24504,"tcp_end":[0.44415,-0.02536,0.15456],"tcp_start":[0.44775,-0.02553,0.04947],"tcp_to_object_dist_end":0.03333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.48433,0.02026,0.13716],"object_pos_start":[0.45209,-0.02594,0.1222],"object_to_goal_dist_end":0.23899,"object_to_goal_dist_start":0.29427,"object_z_max":0.14098,"peak_contact_force":5.34935,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_place","tcp_end":[0.47509,0.01792,0.17845],"tcp_start":[0.47497,0.01773,0.17838],"tcp_to_object_dist_end":0.04237,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.49643,0.03611,0.0335],"object_pos_start":[0.48472,0.02077,0.13617],"object_to_goal_dist_end":0.23236,"object_to_goal_dist_start":0.23826,"object_z_max":0.13617,"peak_contact_force":0.12265,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":750.0,"raw_peak_contact_force":1.55943,"tcp_end":[0.47646,0.02269,0.17332],"tcp_start":[0.47509,0.01792,0.17845],"tcp_to_object_dist_end":0.14188,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50494,0.04688,0.01602],"object_pos_start":[0.49643,0.03611,0.0335],"object_to_goal_dist_end":0.22655,"object_to_goal_dist_start":0.23236,"object_z_max":0.0335,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.47127,0.02248,0.19912],"tcp_start":[0.47646,0.02269,0.17332],"tcp_to_object_dist_end":0.18776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50494,0.04689,0.01602],"object_pos_start":[0.50494,0.04688,0.01602],"object_to_goal_dist_end":0.22654,"object_to_goal_dist_start":0.22655,"object_z_max":0.01602,"peak_contact_force":20.02587,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":636.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46926,0.02237,0.36185],"tcp_start":[0.47127,0.02248,0.19912],"tcp_to_object_dist_end":0.34853,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9507,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11236,"approach_goal.approach_speed":0.11442,"approach_object.approach_height":0.11687,"descend_grasp.descend_offset_z":-0.00998,"descend_place.place_descend_z_offset":0.00943,"descend_place.place_force_threshold":2.94846,"grasp.retry_x":0.00389,"grasp.retry_z":-0.00317,"lift.lift_height":0.13797,"release.release_time":2.47773,"retract.retract_height":0.07937},"optimized_scores":{"best_composite_score":-0.01023,"best_fitness_score":0.59477,"best_task_score":0.26015},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":466.0,"contact_point_centroid":[0.58926,0.07588,-0.0045],"force_p95":0.90745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98574,"mean_force":0.22526,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55555,0.05083,0.23436]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.54146,0.00099,-0.00113],"force_p95":0.32479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4442,"mean_force":0.0658,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52919,0.00086,0.046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12301.0,"contact_point_centroid":[0.53047,0.01976,0.10515],"force_p95":0.09121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32892,"mean_force":0.06542,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52661,0.00083,0.10258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4484.0,"contact_point_centroid":[0.54155,-0.00077,0.1854],"force_p95":0.13506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3127,"mean_force":0.08719,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53551,0.01772,0.18532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4606.0,"contact_point_centroid":[0.54212,0.03684,0.18628],"force_p95":0.13297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31178,"mean_force":0.08538,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53606,0.01837,0.18625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12727.0,"contact_point_centroid":[0.53019,-0.01805,0.10303],"force_p95":0.0914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28791,"mean_force":0.06372,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52663,0.00083,0.10068]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00104,-0.00203],"force_p95":0.13123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14727,"mean_force":0.12526,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53197,0.00092,0.04578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.56713,0.0643,0.22103],"force_p95":0.13437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14294,"mean_force":0.07943,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56007,0.0511,0.22749]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51627,0.00046,0.27335]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58952,0.07585,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1246,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55332,0.05058,0.32975]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53567,0.00097,0.1506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4232.0,"contact_point_centroid":[0.53135,-0.01829,0.04697],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10317,"mean_force":0.0507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53078,0.0009,0.04436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4761.0,"contact_point_centroid":[0.53137,0.01998,0.04637],"force_p95":0.06835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09305,"mean_force":0.04553,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53078,0.0009,0.04436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.56844,0.06392,0.22109],"force_p95":0.04182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04182,"mean_force":0.04182,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5601,0.0512,0.22754]}],"total_contact_groups":14},"final_pose_error":0.01731,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58952,0.07585,0.01602],"final_tcp_position":[0.55412,0.05063,0.41256],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":6.00602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53461,0.00093,0.24878],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1295,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14727,"tcp_end":[0.53907,0.00104,0.05435],"tcp_start":[0.53461,0.00093,0.24878],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00096,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25037,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.08269,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":25168.0,"raw_peak_contact_force":0.4442,"tcp_end":[0.53075,0.00089,0.04433],"tcp_start":[0.53907,0.00104,0.05435],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.5399,0.00089,0.14439],"object_pos_start":[0.54421,0.00096,0.02587],"object_to_goal_dist_end":0.1962,"object_to_goal_dist_start":0.25037,"object_z_max":0.14427,"peak_contact_force":0.00569,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9090.0,"raw_peak_contact_force":0.3127,"tcp_end":[0.52694,0.00084,0.16966],"tcp_start":[0.53075,0.00089,0.04433],"tcp_to_object_dist_end":0.0284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.54271,0.01116,0.15194],"object_pos_start":[0.5399,0.00089,0.14439],"object_to_goal_dist_end":0.18474,"object_to_goal_dist_start":0.1962,"object_z_max":0.19331,"peak_contact_force":6.00602,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":0.14294,"subtask_id":"reach_place","tcp_end":[0.56007,0.0511,0.22749],"tcp_start":[0.53131,0.0113,0.17812],"tcp_to_object_dist_end":0.08721,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.56941,0.05457,0.19043],"object_pos_start":[0.5692,0.05429,0.19084],"object_to_goal_dist_end":0.12974,"object_to_goal_dist_start":0.13009,"object_z_max":0.19084,"peak_contact_force":0.12466,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":467.0,"raw_peak_contact_force":1.98574,"tcp_end":[0.5601,0.0512,0.22754],"tcp_start":[0.56007,0.0511,0.22749],"tcp_to_object_dist_end":0.03841,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58952,0.07584,0.01608],"object_pos_start":[0.56941,0.05457,0.19043],"object_to_goal_dist_end":0.20193,"object_to_goal_dist_start":0.12974,"object_z_max":0.19043,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.1246,"tcp_end":[0.55536,0.05082,0.25046],"tcp_start":[0.5601,0.0512,0.22754],"tcp_to_object_dist_end":0.23817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58952,0.07585,0.01602],"object_pos_start":[0.58952,0.07584,0.01608],"object_to_goal_dist_end":0.20197,"object_to_goal_dist_start":0.20193,"object_z_max":0.01608,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.55412,0.05063,0.41256],"tcp_start":[0.55536,0.05082,0.25046],"tcp_to_object_dist_end":0.39891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```