## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0222 | 0.23 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.0305 | 0.16 | ✅ accepted |
| 5 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 4 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |
| 3 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |

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

## Current Skill (Q=0.022) — your mutation base

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
  retries:
    max_attempts: 0
    strategy: repeat
- id: approach_goal
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
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (add)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
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
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.022
- **task_score** (E): 0.229
- **fitness_score**: 0.577  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0506 |
| descend_grasp | 1.00 | 1.00 | 0.2125 |
| grasp | 1.00 | 1.00 | 0.0113 |
| lift | 1.00 | 1.00 | 0.1015 |
| approach_goal | 0.00 | 1.00 | 0.1966 |
| descend_place | 1.00 | 1.00 | 0.0002 |
| release | 1.00 | 1.00 | 0.0227 |
| retract | 0.00 | 1.00 | 0.1604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.012, 0.268) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.493, -0.012, 0.268)→(0.489, -0.015, 0.055) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 41.667 | 0.138 | 0.172 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.055)→(0.481, -0.015, 0.047) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 24.000 | 0.110 | 0.415 |
| lift | lift | 1.00 / step_budget | (0.481, -0.015, 0.047)→(0.477, -0.015, 0.148) | (0.493, -0.015, 0.026)→(0.488, -0.015, 0.120) | 0.281→0.248 | 1.00 / 8.333 | 0.123 | 1.808 |
| approach_goal | approach | 0.00 / step_budget | (0.477, -0.015, 0.148)→(0.564, 0.092, 0.288) | (0.488, -0.015, 0.120)→(0.540, 0.051, 0.016) | 0.248→0.221 | 1.00 / 8.667 | 185264.609 | 0.123 |
| descend_place | descend | 1.00 / force_exceeded | (0.564, 0.092, 0.288)→(0.564, 0.092, 0.288) | (0.540, 0.051, 0.016)→(0.540, 0.051, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.564, 0.092, 0.288)→(0.561, 0.092, 0.310) | (0.540, 0.051, 0.016)→(0.540, 0.051, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 0.00 / step_budget | (0.561, 0.092, 0.310)→(0.560, 0.091, 0.471) | (0.540, 0.051, 0.016)→(0.540, 0.051, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.122 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.241
- phase_score: 0.000
- phase_breakdown.reach_place_score: 0.000
- phase_breakdown.reach_grasp_score: 0.000
- grasp_place_fitness: 0.584

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.584
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.241
- **Median Q (composite search score)**: 0.025
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92105,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.17327,"approach_goal.approach_speed":0.24866,"approach_object.approach_height":0.16912,"descend_grasp.descend_offset_z":-0.00996,"descend_place.place_descend_z_offset":0.00489,"descend_place.place_force_threshold":7.56539,"grasp.retry_x":0.00085,"grasp.retry_z":0.0043,"lift.lift_height":0.11325,"retract.retract_height":0.12558},"optimized_scores":{"best_composite_score":0.01243,"best_fitness_score":0.56743,"best_task_score":0.21001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1765.0,"contact_point_centroid":[0.52635,0.043,-0.00262],"force_p95":0.25994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85508,"mean_force":0.1493,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52638,0.05157,0.26852]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.47348,-0.01898,-0.00113],"force_p95":0.3088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39579,"mean_force":0.05305,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46355,-0.01945,0.04927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5159.0,"contact_point_centroid":[0.4827,-0.01822,0.17928],"force_p95":0.13286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31065,"mean_force":0.08277,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47691,0.00021,0.17953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9783.0,"contact_point_centroid":[0.46341,-0.00041,0.09356],"force_p95":0.1029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29698,"mean_force":0.0664,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46115,-0.01938,0.09302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10905.0,"contact_point_centroid":[0.46308,-0.03825,0.09321],"force_p95":0.09738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28952,"mean_force":0.0605,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46116,-0.01938,0.09263]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5275.0,"contact_point_centroid":[0.48391,0.01986,0.18098],"force_p95":0.12696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21412,"mean_force":0.08276,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.478,0.00137,0.1815]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02008,-0.00206],"force_p95":0.14026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18109,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46598,-0.01951,0.0486]},{"body_a":"world","body_b":"grasp_target","contact_count":392.0,"contact_point_centroid":[0.47616,-0.02015,-0.00168],"force_p95":0.13818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12392,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49091,-0.0062,0.2971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.4658,-0.00027,0.04876],"force_p95":0.07795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13632,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46492,-0.01949,0.04752]},{"body_a":"world","body_b":"grasp_target","contact_count":2976.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47617,-0.01646,0.1738]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5264,0.04304,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54583,0.07148,0.3032]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5264,0.04304,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54338,0.07131,0.30597]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5264,0.04304,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5413,0.07091,0.40448]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4906.0,"contact_point_centroid":[0.46497,-0.03856,0.04876],"force_p95":0.06934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08432,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46492,-0.01949,0.04752]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1672.0,"contact_point_centroid":[0.52857,0.05381,0.27475],"force_p95":0.01229,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01586,"mean_force":0.01064,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52855,0.0538,0.2724]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.54521,0.07163,0.30359],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54502,0.07163,0.30112]}],"total_contact_groups":17},"final_pose_error":0.06585,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.5264,0.04304,0.01602],"final_tcp_position":[0.54219,0.07099,0.4861],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273084.02996,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":99.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02601],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2976.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.48192,-0.01332,0.29497],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02601],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28839,"object_z_max":0.02602,"peak_contact_force":0.13847,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.18109,"tcp_end":[0.47237,-0.01966,0.05522],"tcp_start":[0.48192,-0.01332,0.29497],"tcp_to_object_dist_end":0.02945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01962,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.09599,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20814.0,"raw_peak_contact_force":0.39579,"tcp_end":[0.46489,-0.01948,0.04749],"tcp_start":[0.47237,-0.01966,0.05522],"tcp_to_object_dist_end":0.02443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.47196,-0.01972,0.12135],"object_pos_start":[0.47609,-0.01962,0.02578],"object_to_goal_dist_end":0.2493,"object_to_goal_dist_start":0.28823,"object_z_max":0.12123,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13871.0,"raw_peak_contact_force":1.85508,"tcp_end":[0.46118,-0.01936,0.14944],"tcp_start":[0.46489,-0.01948,0.04749],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5264,0.04304,0.01602],"object_pos_start":[0.47196,-0.01972,0.12135],"object_to_goal_dist_end":0.23409,"object_to_goal_dist_start":0.2493,"object_z_max":0.1846,"peak_contact_force":273084.02996,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54583,0.07148,0.3032],"tcp_start":[0.46118,-0.01936,0.14944],"tcp_to_object_dist_end":0.28924,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5264,0.04304,0.01602],"object_pos_start":[0.5264,0.04304,0.01602],"object_to_goal_dist_end":0.23409,"object_to_goal_dist_start":0.23409,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54589,0.07157,0.30328],"tcp_start":[0.54583,0.07148,0.3032],"tcp_to_object_dist_end":0.28933,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5264,0.04304,0.01602],"object_pos_start":[0.5264,0.04304,0.01602],"object_to_goal_dist_end":0.23409,"object_to_goal_dist_start":0.23409,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54252,0.07114,0.32636],"tcp_start":[0.54589,0.07157,0.30328],"tcp_to_object_dist_end":0.31203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5264,0.04304,0.01602],"object_pos_start":[0.5264,0.04304,0.01602],"object_to_goal_dist_end":0.23409,"object_to_goal_dist_start":0.23409,"object_z_max":0.01602,"peak_contact_force":0.12222,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":392.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.54219,0.07099,0.4861],"tcp_start":[0.54252,0.07114,0.32636],"tcp_to_object_dist_end":0.47118,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05797,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.19926,"approach_goal.approach_speed":0.27874,"approach_object.approach_height":0.08415,"descend_grasp.descend_offset_z":-0.00998,"descend_place.place_descend_z_offset":-0.00638,"descend_place.place_force_threshold":5.23243,"grasp.retry_x":0.00276,"grasp.retry_z":0.0078,"lift.lift_height":0.10732,"retract.retract_height":0.16627},"optimized_scores":{"best_composite_score":0.0253,"best_fitness_score":0.5803,"best_task_score":0.23637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1933.0,"contact_point_centroid":[0.51695,0.05201,-0.00251],"force_p95":0.21887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8028,"mean_force":0.14697,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52235,0.07606,0.25557]},{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.45604,-0.02496,-0.00112],"force_p95":0.31927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38612,"mean_force":0.04844,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4463,-0.02552,0.04969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9148.0,"contact_point_centroid":[0.44591,-0.00646,0.0902],"force_p95":0.12798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29336,"mean_force":0.06964,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44397,-0.02542,0.09004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10382.0,"contact_point_centroid":[0.44584,-0.04419,0.09111],"force_p95":0.09906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28649,"mean_force":0.06008,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44397,-0.02542,0.09068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4515.0,"contact_point_centroid":[0.46697,-0.01813,0.16882],"force_p95":0.13229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26536,"mean_force":0.08651,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4612,-0.00012,0.16939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3691.0,"contact_point_centroid":[0.46844,0.02039,0.16933],"force_p95":0.13869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23111,"mean_force":0.10529,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46291,0.00203,0.1718]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02625,-0.00206],"force_p95":0.14173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18324,"mean_force":0.12756,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44865,-0.02561,0.0489]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.45856,-0.02632,-0.00187],"force_p95":0.1366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48106,-0.01059,0.26155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.4485,-0.00636,0.049],"force_p95":0.0783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13675,"mean_force":0.05213,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44762,-0.02557,0.0479]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45729,-0.02395,0.13796]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51703,0.05203,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54822,0.10795,0.29178]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51703,0.05203,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54568,0.10766,0.29454]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51703,0.05203,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54347,0.10706,0.39332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.44766,-0.04465,0.04902],"force_p95":0.06968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08004,"mean_force":0.04438,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44762,-0.02557,0.0479]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1832.0,"contact_point_centroid":[0.52525,0.07974,0.26198],"force_p95":0.01147,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52532,0.07973,0.25974]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.54768,0.10814,0.29213],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.0102,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5474,0.10813,0.2898]}],"total_contact_groups":17},"final_pose_error":0.10577,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51703,0.05203,0.01602],"final_tcp_position":[0.54436,0.10718,0.47536],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.98149,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46206,-0.0222,0.22246],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13979,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10817.0,"raw_peak_contact_force":0.18324,"tcp_end":[0.45483,-0.02584,0.05504],"tcp_start":[0.46206,-0.0222,0.22246],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02574,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13659,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19655.0,"raw_peak_contact_force":0.38612,"tcp_end":[0.44759,-0.02557,0.04787],"tcp_start":[0.45483,-0.02584,0.05504],"tcp_to_object_dist_end":0.02465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.4543,-0.02629,0.11486],"object_pos_start":[0.4585,-0.02574,0.02576],"object_to_goal_dist_end":0.29311,"object_to_goal_dist_start":0.30331,"object_z_max":0.11475,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11971.0,"raw_peak_contact_force":1.8028,"tcp_end":[0.44393,-0.0254,0.14426],"tcp_start":[0.44759,-0.02557,0.04787],"tcp_to_object_dist_end":0.03119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51703,0.05203,0.01602],"object_pos_start":[0.4543,-0.02629,0.11486],"object_to_goal_dist_end":0.21635,"object_to_goal_dist_start":0.29311,"object_z_max":0.16966,"peak_contact_force":9748.98149,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54822,0.10795,0.29178],"tcp_start":[0.44393,-0.0254,0.14426],"tcp_to_object_dist_end":0.2831,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51703,0.05203,0.01602],"object_pos_start":[0.51703,0.05203,0.01602],"object_to_goal_dist_end":0.21635,"object_to_goal_dist_start":0.21635,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54827,0.10806,0.29191],"tcp_start":[0.54822,0.10795,0.29178],"tcp_to_object_dist_end":0.28325,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51703,0.05203,0.01602],"object_pos_start":[0.51703,0.05203,0.01602],"object_to_goal_dist_end":0.21635,"object_to_goal_dist_start":0.21635,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54477,0.1074,0.31486],"tcp_start":[0.54827,0.10806,0.29191],"tcp_to_object_dist_end":0.30519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51703,0.05203,0.01602],"object_pos_start":[0.51703,0.05203,0.01602],"object_to_goal_dist_end":0.21635,"object_to_goal_dist_start":0.21635,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.54436,0.10718,0.47536],"tcp_start":[0.54477,0.1074,0.31486],"tcp_to_object_dist_end":0.46345,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92763,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.06376,"approach_goal.approach_speed":0.20925,"approach_object.approach_height":0.1602,"descend_grasp.descend_offset_z":-0.0089,"descend_place.place_descend_z_offset":0.00043,"descend_place.place_force_threshold":4.55754,"grasp.retry_x":0.00911,"grasp.retry_z":0.0027,"lift.lift_height":0.11868,"retract.retract_height":0.16837},"optimized_scores":{"best_composite_score":0.02902,"best_fitness_score":0.58402,"best_task_score":0.24139},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2090.0,"contact_point_centroid":[0.57746,0.05866,-0.00248],"force_p95":0.18127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76534,"mean_force":0.14389,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57916,0.07241,0.23755]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.54164,0.00051,-0.00112],"force_p95":0.30863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46174,"mean_force":0.06322,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52938,0.00087,0.04731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10388.0,"contact_point_centroid":[0.52983,0.01967,0.0932],"force_p95":0.09929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3227,"mean_force":0.06571,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52683,0.00084,0.0916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9970.0,"contact_point_centroid":[0.52942,-0.01805,0.092],"force_p95":0.10572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28631,"mean_force":0.06788,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52685,0.00084,0.09087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3786.0,"contact_point_centroid":[0.54336,0.0002,0.17003],"force_p95":0.15704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26247,"mean_force":0.09396,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53767,0.01876,0.16981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4399.0,"contact_point_centroid":[0.54489,0.03871,0.17193],"force_p95":0.12962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21226,"mean_force":0.08168,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53888,0.0204,0.17179]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00114,-0.00203],"force_p95":0.13368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15203,"mean_force":0.12536,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53217,0.00092,0.04707]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51807,0.0005,0.29098]},{"body_a":"world","body_b":"grasp_target","contact_count":2724.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53642,0.00099,0.16934]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.57751,0.05866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59851,0.09713,0.269]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57751,0.05866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59554,0.09672,0.27017]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.57751,0.05866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59304,0.09612,0.3682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4603.0,"contact_point_centroid":[0.53111,-0.01828,0.0473],"force_p95":0.07107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10561,"mean_force":0.04724,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53098,0.0009,0.04565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.53194,0.02006,0.04877],"force_p95":0.06882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08496,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53098,0.0009,0.04565]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1995.0,"contact_point_centroid":[0.5812,0.075,0.24324],"force_p95":0.01191,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01457,"mean_force":0.01058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58118,0.075,0.24085]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.59757,0.09717,0.26835],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01029,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59744,0.09717,0.26609]}],"total_contact_groups":17},"final_pose_error":0.10755,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57751,0.05866,0.01602],"final_tcp_position":[0.59402,0.09624,0.45083],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272960.81598,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2724.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53566,0.00094,0.28532],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13432,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11219.0,"raw_peak_contact_force":0.15203,"tcp_end":[0.53924,0.00105,0.05563],"tcp_start":[0.53566,0.00094,0.28532],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00099,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25035,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.09785,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20499.0,"raw_peak_contact_force":0.46174,"tcp_end":[0.53095,0.0009,0.04561],"tcp_start":[0.53924,0.00105,0.05563],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53851,0.00111,0.12519],"object_pos_start":[0.54422,0.00099,0.02586],"object_to_goal_dist_end":0.20222,"object_to_goal_dist_start":0.25035,"object_z_max":0.12507,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12270.0,"raw_peak_contact_force":1.76534,"tcp_end":[0.52698,0.00085,0.15168],"tcp_start":[0.53095,0.0009,0.04561],"tcp_to_object_dist_end":0.02889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57751,0.05866,0.01602],"object_pos_start":[0.53851,0.00111,0.12519],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.20222,"object_z_max":0.16408,"peak_contact_force":272960.81598,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59851,0.09709,0.26901],"tcp_start":[0.52698,0.00085,0.15168],"tcp_to_object_dist_end":0.25675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.57751,0.05866,0.01602],"object_pos_start":[0.57751,0.05866,0.01602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.2132,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59853,0.09722,0.26893],"tcp_start":[0.59851,0.09709,0.26901],"tcp_to_object_dist_end":0.25669,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57751,0.05866,0.01602],"object_pos_start":[0.57751,0.05866,0.01602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.2132,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59449,0.09648,0.29001],"tcp_start":[0.59853,0.09722,0.26893],"tcp_to_object_dist_end":0.27711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57751,0.05866,0.01602],"object_pos_start":[0.57751,0.05866,0.01602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.2132,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59402,0.09624,0.45083],"tcp_start":[0.59449,0.09648,0.29001],"tcp_to_object_dist_end":0.43675,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```