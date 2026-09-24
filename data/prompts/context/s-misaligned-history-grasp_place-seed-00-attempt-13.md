## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19  | -0.1287 | 0.76 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | -0.0249 | 0.95 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.0190 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 16  | -0.0266 | 0.95 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | -0.3652 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.954, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=-0.365) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.15
- id: lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.15
- id: place
  weight: 0.2
- id: place_fine
  offset:
  - 0.01
  - 0.0
  - 0.02
  weight: 0.3
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
      mode: keep_current
  parameters:
    approach_height:
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
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_grasp
- id: descend_to_grasp
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
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp
- id: grasp_action
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_max_width:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: guards.check_grasp.threshold
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.04
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: lift
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place
- id: fine_placement
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.01
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.x
        mode: replace
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_fine

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_max_width: status=consumed; consumers=guards.check_grasp.threshold (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.04
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **fine_placement** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.01, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_offset_y: status=consumed; consumers=target.offset.y (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.365
- **task_score** (E): 0.331
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1402 |
| descend_to_grasp | 1.00 | 1.00 | 0.1142 |
| grasp_action | 1.00 | 1.00 | 0.0119 |
| lift_object | 0.33 | 1.00 | 0.1328 |
| transport_to_goal | 0.33 | 1.00 | 0.1674 |
| raise_for_release | 1.00 | 0.67 | 0.0455 |
| release_action | 1.00 | 1.00 | 0.0221 |
| retract_after_release | 0.00 | 1.00 | 0.0294 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.000, 0.163) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.497, 0.000, 0.163)→(0.493, 0.000, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.493, 0.000, 0.049)→(0.485, 0.000, 0.041) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 45.333 | 0.156 | 0.216 |
| lift_object | lift | 0.33 / step_budget | (0.485, 0.000, 0.041)→(0.483, 0.000, 0.173) | (0.497, 0.000, 0.026)→(0.500, 0.000, 0.155) | 0.266→0.212 | 1.00 / 26.667 | 0.113 | 0.539 |
| transport_to_goal | approach | 0.33 / step_budget | (0.483, 0.000, 0.173)→(0.561, 0.143, 0.179) | (0.500, 0.000, 0.155)→(0.573, 0.142, 0.155) | 0.212→0.057 | 1.00 / 24.000 | 0.125 | 0.289 |
| raise_for_release | approach | 1.00 / step_budget | (0.561, 0.143, 0.179)→(0.575, 0.172, 0.207) | (0.573, 0.142, 0.155)→(0.590, 0.174, 0.177) | 0.057→0.019 | 0.67 / 15.000 | 0.080 | 0.475 |
| release_action | release | 1.00 / step_budget | (0.575, 0.172, 0.207)→(0.570, 0.170, 0.229) | (0.590, 0.174, 0.177)→(0.589, 0.181, 0.017) | 0.019→0.172 | 1.00 / 2.667 | 0.209 | 1.902 |
| retract_after_release | retract | 0.00 / step_budget | (0.570, 0.170, 0.229)→(0.569, 0.170, 0.258) | (0.589, 0.181, 0.017)→(0.595, 0.185, 0.019) | 0.172→0.170 | 1.00 / 3.333 | 0.201 | 0.249 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.432
- phase_score: 0.436
- phase_breakdown.lift_score: 0.255
- phase_breakdown.place_score: 0.304
- phase_breakdown.pre_grasp_score: 0.472
- phase_breakdown.place_fine_score: 0.431
- phase_breakdown.grasp_score: 0.759
- grasp_place_fitness: 0.680

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.680
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.432
- **Median Q (composite search score)**: -0.371
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.descend_tolerance
- **Final σ (mean)**: 0.317


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19149,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.0856,"approach_object.approach_speed":0.1787,"approach_object.approach_tolerance":0.02536,"descend_to_grasp.descend_speed":0.16305,"descend_to_grasp.descend_tolerance":0.01,"descend_to_grasp.grasp_offset_z":0.01325,"grasp_action.grasp_max_width":0.03924,"lift_object.lift_height":0.20375,"lift_object.lift_speed":0.15147,"lift_object.lift_tolerance":0.0598,"raise_for_release.raise_offset_z":0.05168,"raise_for_release.raise_speed":0.07246,"raise_for_release.raise_tolerance":0.02391,"release_action.release_time":0.70471,"retract_after_release.retract_height":0.07592,"retract_after_release.retract_speed":0.12408,"retract_after_release.retract_tolerance":0.07171,"transport_to_goal.transport_speed":0.13391,"transport_to_goal.transport_tolerance":0.03898},"optimized_scores":{"best_composite_score":-0.40444,"best_fitness_score":0.59556,"best_task_score":0.24906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":453.0,"contact_point_centroid":[0.57851,0.17318,-0.00484],"force_p95":0.97474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.35681,"mean_force":0.23794,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.54467,0.14243,0.25908]},{"body_a":"world","body_b":"grasp_target","contact_count":59.0,"contact_point_centroid":[0.50983,-0.02216,-0.00154],"force_p95":0.545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55219,"mean_force":0.29209,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49834,-0.02215,0.03965]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1521.0,"contact_point_centroid":[0.55022,0.14763,0.22647],"force_p95":0.16542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37417,"mean_force":0.09546,"phase_index":5.0,"phase_name":"raise_for_release","phase_type":"approach","tcp_position_centroid":[0.54391,0.12952,0.22593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.49919,-0.00295,0.09935],"force_p95":0.15922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35498,"mean_force":0.07891,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49746,-0.02211,0.09652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2511.0,"contact_point_centroid":[0.4992,-0.04117,0.09767],"force_p95":0.14136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32353,"mean_force":0.07369,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49743,-0.02211,0.09566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.54951,0.10963,0.22464],"force_p95":0.17949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27558,"mean_force":0.11595,"phase_index":5.0,"phase_name":"raise_for_release","phase_type":"approach","tcp_position_centroid":[0.5435,0.1282,0.22347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2226.0,"contact_point_centroid":[0.52542,0.0261,0.19719],"force_p95":0.12612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2051,"mean_force":0.09332,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52007,0.04476,0.19534]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02286,-0.00207],"force_p95":0.14401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19452,"mean_force":0.12837,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50149,-0.02223,0.03985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.52636,0.06609,0.19717],"force_p95":0.11334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14855,"mean_force":0.0852,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52088,0.04757,0.19574]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.5137,-0.02302,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50376,-0.00921,0.22165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.50093,-0.00299,0.04133],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13385,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50032,-0.0222,0.03857]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.57838,0.17296,-0.00198],"force_p95":0.12538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12564,"mean_force":0.12428,"phase_index":7.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.5439,0.14226,0.27739]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50715,-0.02074,0.09263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4930.0,"contact_point_centroid":[0.50097,-0.0413,0.04039],"force_p95":0.07055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07761,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50032,-0.0222,0.03858]}],"total_contact_groups":14},"final_pose_error":0.06715,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.57837,0.17298,0.016],"final_tcp_position":[0.54305,0.142,0.28361],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":2.35681,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":960.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50853,-0.01916,0.13998],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp","tcp_end":[0.50847,-0.02238,0.0476],"tcp_start":[0.50853,-0.01916,0.13998],"tcp_to_object_dist_end":0.02221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02223,0.02574],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26531,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13992,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.19452,"tcp_end":[0.50029,-0.0222,0.03854],"tcp_start":[0.50847,-0.02238,0.0476],"tcp_to_object_dist_end":0.01847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":140.0,"n_steps_budget":840.0,"object_pos_end":[0.51954,-0.02214,0.1692],"object_pos_start":[0.51361,-0.02223,0.02574],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.26531,"object_z_max":0.16811,"peak_contact_force":0.11525,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4838.0,"raw_peak_contact_force":0.55219,"subtask_id":"lift","tcp_end":[0.50008,-0.02213,0.18324],"tcp_start":[0.50029,-0.0222,0.03854],"tcp_to_object_dist_end":0.02399,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.55922,0.11803,0.18946],"object_pos_start":[0.51954,-0.02214,0.1692],"object_to_goal_dist_end":0.04706,"object_to_goal_dist_start":0.18489,"object_z_max":0.18935,"peak_contact_force":0.10705,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4602.0,"raw_peak_contact_force":0.2051,"subtask_id":"place","tcp_end":[0.54199,0.11787,0.20832],"tcp_start":[0.50008,-0.02213,0.18324],"tcp_to_object_dist_end":0.02554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.56936,0.1492,0.21595],"object_pos_start":[0.55922,0.11803,0.18946],"object_to_goal_dist_end":0.0166,"object_to_goal_dist_start":0.04706,"object_z_max":0.22108,"peak_contact_force":0.0,"phase_name":"raise_for_release","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2561.0,"raw_peak_contact_force":0.37417,"subtask_id":"place_fine","tcp_end":[0.54859,0.14336,0.25204],"tcp_start":[0.54199,0.11787,0.20832],"tcp_to_object_dist_end":0.04205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57835,0.17301,0.01612],"object_pos_start":[0.56936,0.1492,0.21595],"object_to_goal_dist_end":0.20839,"object_to_goal_dist_start":0.0166,"object_z_max":0.21595,"peak_contact_force":0.12575,"phase_name":"release_action","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":453.0,"raw_peak_contact_force":2.35681,"tcp_end":[0.54455,0.14239,0.27483],"tcp_start":[0.54859,0.14336,0.25204],"tcp_to_object_dist_end":0.2627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.57837,0.17298,0.016],"object_pos_start":[0.57835,0.17301,0.01612],"object_to_goal_dist_end":0.20851,"object_to_goal_dist_start":0.20839,"object_z_max":0.01612,"peak_contact_force":0.1237,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12564,"tcp_end":[0.54305,0.142,0.28361],"tcp_start":[0.54455,0.14239,0.27483],"tcp_to_object_dist_end":0.2717,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15278,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09737,"approach_object.approach_speed":0.18709,"approach_object.approach_tolerance":0.0402,"descend_to_grasp.descend_speed":0.10561,"descend_to_grasp.descend_tolerance":0.01852,"descend_to_grasp.grasp_offset_z":0.01019,"grasp_action.grasp_max_width":0.02232,"lift_object.lift_height":0.1715,"lift_object.lift_speed":0.13238,"lift_object.lift_tolerance":0.05349,"raise_for_release.raise_offset_z":0.0273,"raise_for_release.raise_speed":0.09553,"raise_for_release.raise_tolerance":0.03408,"release_action.release_time":0.60643,"retract_after_release.retract_height":0.07421,"retract_after_release.retract_speed":0.11891,"retract_after_release.retract_tolerance":0.08311,"transport_to_goal.transport_speed":0.15156,"transport_to_goal.transport_tolerance":0.06041},"optimized_scores":{"best_composite_score":-0.32004,"best_fitness_score":0.67996,"best_task_score":0.43178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.55164,0.21967,-0.00865],"force_p95":1.17978,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48267,"mean_force":0.49483,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.54739,0.21768,0.1668]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.49792,0.04267,-0.00181],"force_p95":0.47336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52353,"mean_force":0.21852,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4869,0.04177,0.04596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.55288,0.22247,0.14983],"force_p95":0.18309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48986,"mean_force":0.10256,"phase_index":5.0,"phase_name":"raise_for_release","phase_type":"approach","tcp_position_centroid":[0.54761,0.20371,0.14881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":769.0,"contact_point_centroid":[0.55337,0.18579,0.15149],"force_p95":0.13868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38606,"mean_force":0.08855,"phase_index":5.0,"phase_name":"raise_for_release","phase_type":"approach","tcp_position_centroid":[0.54784,0.20439,0.14908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2744.0,"contact_point_centroid":[0.4869,0.06077,0.09813],"force_p95":0.12917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35059,"mean_force":0.06653,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48606,0.0416,0.09564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.48677,0.02237,0.09836],"force_p95":0.1438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31334,"mean_force":0.07324,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48608,0.0416,0.09619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1618.0,"contact_point_centroid":[0.51866,0.08743,0.15889],"force_p95":0.15013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30985,"mean_force":0.09354,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51383,0.10626,0.15682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.55665,0.23872,0.15327],"force_p95":0.12649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2536,"mean_force":0.07527,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.55125,0.21963,0.15248]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50129,0.04485,-0.00225],"force_p95":0.19098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25025,"mean_force":0.14068,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48994,0.04204,0.04599]},{"body_a":"world","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.54922,0.22004,-0.00287],"force_p95":0.22658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22981,"mean_force":0.14529,"phase_index":7.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.54649,0.21737,0.17967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.5575,0.20112,0.15516],"force_p95":0.09253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21782,"mean_force":0.0586,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.55133,0.21968,0.1526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1678.0,"contact_point_centroid":[0.51978,0.12771,0.15786],"force_p95":0.12811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19393,"mean_force":0.08614,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51485,0.10912,0.15638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4788.0,"contact_point_centroid":[0.4881,0.02265,0.04718],"force_p95":0.07569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15973,"mean_force":0.04524,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48882,0.04194,0.04479]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.50118,0.04505,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5001,0.01574,0.2358]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49728,0.03793,0.10883]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5859.0,"contact_point_centroid":[0.48833,0.06128,0.04771],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07862,"mean_force":0.03897,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48882,0.04194,0.0448]}],"total_contact_groups":16},"final_pose_error":0.06646,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56928,0.21495,0.0245],"final_tcp_position":[0.54521,0.21682,0.18509],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.48267,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":580.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49968,0.03335,0.16567],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":880.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp","tcp_end":[0.49704,0.04261,0.05395],"tcp_start":[0.49968,0.03335,0.16567],"tcp_to_object_dist_end":0.02834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50121,0.04296,0.0251],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24406,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.18496,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12447.0,"raw_peak_contact_force":0.25025,"tcp_end":[0.48879,0.04193,0.04476],"tcp_start":[0.49704,0.04261,0.05395],"tcp_to_object_dist_end":0.02327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":130.0,"n_steps_budget":810.0,"object_pos_end":[0.50502,0.04253,0.14265],"object_pos_start":[0.50121,0.04296,0.0251],"object_to_goal_dist_end":0.21091,"object_to_goal_dist_start":0.24406,"object_z_max":0.14169,"peak_contact_force":0.11205,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5119.0,"raw_peak_contact_force":0.52353,"subtask_id":"lift","tcp_end":[0.48769,0.04165,0.16307],"tcp_start":[0.48879,0.04193,0.04476],"tcp_to_object_dist_end":0.0268,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":137.0,"n_steps_budget":1000.0,"object_pos_end":[0.56118,0.18905,0.12398],"object_pos_start":[0.50502,0.04253,0.14265],"object_to_goal_dist_end":0.06037,"object_to_goal_dist_start":0.21091,"object_z_max":0.14734,"peak_contact_force":0.11367,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3296.0,"raw_peak_contact_force":0.30985,"subtask_id":"place","tcp_end":[0.54441,0.1888,0.146],"tcp_start":[0.48769,0.04165,0.16307],"tcp_to_object_dist_end":0.02768,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.56873,0.22027,0.13225],"object_pos_start":[0.56118,0.18905,0.12398],"object_to_goal_dist_end":0.02889,"object_to_goal_dist_start":0.06037,"object_z_max":0.13205,"peak_contact_force":0.10833,"phase_name":"raise_for_release","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1513.0,"raw_peak_contact_force":0.48986,"subtask_id":"place_fine","tcp_end":[0.55301,0.21933,0.15526],"tcp_start":[0.54441,0.1888,0.146],"tcp_to_object_dist_end":0.02789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56218,0.21325,0.026],"object_pos_start":[0.56873,0.22027,0.13225],"object_to_goal_dist_end":0.12486,"object_to_goal_dist_start":0.02889,"object_z_max":0.13254,"peak_contact_force":0.23151,"phase_name":"release_action","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1793.0,"raw_peak_contact_force":1.48267,"tcp_end":[0.5473,0.21765,0.17731],"tcp_start":[0.55301,0.21933,0.15526],"tcp_to_object_dist_end":0.1521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.56928,0.21495,0.0245],"object_pos_start":[0.56218,0.21325,0.026],"object_to_goal_dist_end":0.12598,"object_to_goal_dist_start":0.12486,"object_z_max":0.02628,"peak_contact_force":0.18243,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":40.0,"raw_peak_contact_force":0.22981,"tcp_end":[0.54521,0.21682,0.18509],"tcp_start":[0.5473,0.21765,0.17731],"tcp_to_object_dist_end":0.1624,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39113,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11281,"approach_object.approach_speed":0.21369,"approach_object.approach_tolerance":0.04218,"descend_to_grasp.descend_speed":0.0215,"descend_to_grasp.descend_tolerance":0.01097,"descend_to_grasp.grasp_offset_z":0.01003,"grasp_action.grasp_max_width":0.0207,"lift_object.lift_height":0.15057,"lift_object.lift_speed":0.11674,"lift_object.lift_tolerance":0.01559,"raise_for_release.raise_offset_z":0.04063,"raise_for_release.raise_speed":0.08648,"raise_for_release.raise_tolerance":0.02,"release_action.release_time":0.46106,"retract_after_release.retract_height":0.13906,"retract_after_release.retract_speed":0.09146,"retract_after_release.retract_tolerance":0.06916,"transport_to_goal.transport_speed":0.17683,"transport_to_goal.transport_tolerance":0.05251},"optimized_scores":{"best_composite_score":-0.37123,"best_fitness_score":0.62877,"best_task_score":0.31134},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.6253,0.15366,-0.01278],"force_p95":1.79351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86526,"mean_force":0.87566,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.61785,0.15113,0.2268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2502.0,"contact_point_centroid":[0.61084,0.15483,0.19302],"force_p95":0.13475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56214,"mean_force":0.08389,"phase_index":5.0,"phase_name":"raise_for_release","phase_type":"approach","tcp_position_centroid":[0.60854,0.13664,0.19492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2211.0,"contact_point_centroid":[0.61254,0.11865,0.19343],"force_p95":0.14115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55774,"mean_force":0.09172,"phase_index":5.0,"phase_name":"raise_for_release","phase_type":"approach","tcp_position_centroid":[0.60892,0.13708,0.19543]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.47351,-0.01914,-0.00134],"force_p95":0.52538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5413,"mean_force":0.09937,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46355,-0.01925,0.0399]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.63201,0.15413,-0.00363],"force_p95":0.31468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39284,"mean_force":0.16259,"phase_index":7.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.61708,0.15079,0.26609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2369.0,"contact_point_centroid":[0.53447,0.03211,0.17774],"force_p95":0.16528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35259,"mean_force":0.09579,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53003,0.05096,0.1772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8793.0,"contact_point_centroid":[0.46358,-0.03806,0.09815],"force_p95":0.10509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28395,"mean_force":0.06536,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46117,-0.01917,0.09643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8225.0,"contact_point_centroid":[0.46355,-0.00021,0.09925],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28241,"mean_force":0.06881,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46118,-0.01917,0.09704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":685.0,"contact_point_centroid":[0.62585,0.17052,0.20817],"force_p95":0.13645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25435,"mean_force":0.08709,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.62115,0.15221,0.21046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":499.0,"contact_point_centroid":[0.62584,0.13414,0.20786],"force_p95":0.13971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24055,"mean_force":0.09165,"phase_index":6.0,"phase_name":"release_action","phase_type":"release","tcp_position_centroid":[0.62129,0.15226,0.21076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2470.0,"contact_point_centroid":[0.53458,0.06965,0.17747],"force_p95":0.14396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21195,"mean_force":0.08672,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53029,0.05123,0.17721]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02005,-0.00208],"force_p95":0.14467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20232,"mean_force":0.12865,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46584,-0.0193,0.0396]},{"body_a":"world","body_b":"grasp_target","contact_count":476.0,"contact_point_centroid":[0.47616,-0.02015,-0.00174],"force_p95":0.13801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12366,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49207,-0.00663,0.2451]},{"body_a":"world","body_b":"grasp_target","contact_count":1768.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47599,-0.01678,0.11325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5301.0,"contact_point_centroid":[0.46416,-2e-05,0.04014],"force_p95":0.06577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11186,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46474,-0.01927,0.03849]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5428.0,"contact_point_centroid":[0.46416,-0.03856,0.04001],"force_p95":0.06591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07215,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46474,-0.01927,0.0385]}],"total_contact_groups":16},"final_pose_error":0.06795,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63884,0.16778,0.01535],"final_tcp_position":[0.6181,0.15089,0.30513],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.86526,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12253,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48256,-0.01417,0.18391],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1768.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp","tcp_end":[0.47247,-0.01943,0.04632],"tcp_start":[0.48256,-0.01417,0.18391],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01948,0.02572],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28819,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14221,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12529.0,"raw_peak_contact_force":0.20232,"tcp_end":[0.46471,-0.01927,0.03847],"tcp_start":[0.47247,-0.01943,0.04632],"tcp_to_object_dist_end":0.01708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":550.0,"n_steps_budget":810.0,"object_pos_end":[0.47637,-0.01918,0.15286],"object_pos_start":[0.47608,-0.01948,0.02572],"object_to_goal_dist_end":0.23925,"object_to_goal_dist_start":0.28819,"object_z_max":0.15268,"peak_contact_force":0.11075,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17105.0,"raw_peak_contact_force":0.5413,"subtask_id":"lift","tcp_end":[0.46127,-0.01916,0.17394],"tcp_start":[0.46471,-0.01927,0.03847],"tcp_to_object_dist_end":0.02593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.5984,0.12002,0.15085],"object_pos_start":[0.47637,-0.01918,0.15286],"object_to_goal_dist_end":0.06449,"object_to_goal_dist_start":0.23925,"object_z_max":0.15296,"peak_contact_force":0.15514,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4839.0,"raw_peak_contact_force":0.35259,"subtask_id":"place","tcp_end":[0.59682,0.12113,0.18129],"tcp_start":[0.46127,-0.01916,0.17394],"tcp_to_object_dist_end":0.0305,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.63076,0.15307,0.18165],"object_pos_start":[0.5984,0.12002,0.15085],"object_to_goal_dist_end":0.01038,"object_to_goal_dist_start":0.06449,"object_z_max":0.18152,"peak_contact_force":0.13135,"phase_name":"raise_for_release","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4713.0,"raw_peak_contact_force":0.56214,"subtask_id":"place_fine","tcp_end":[0.62272,0.15239,0.21422],"tcp_start":[0.59682,0.12113,0.18129],"tcp_to_object_dist_end":0.03355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62789,0.15601,0.008],"object_pos_start":[0.63076,0.15307,0.18165],"object_to_goal_dist_end":0.18207,"object_to_goal_dist_start":0.01038,"object_z_max":0.1817,"peak_contact_force":0.27039,"phase_name":"release_action","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1273.0,"raw_peak_contact_force":1.86526,"tcp_end":[0.61782,0.15112,0.23401],"tcp_start":[0.62272,0.15239,0.21422],"tcp_to_object_dist_end":0.22628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":73.0,"n_steps_budget":960.0,"object_pos_end":[0.63884,0.16778,0.01535],"object_pos_start":[0.62789,0.15601,0.008],"object_to_goal_dist_end":0.17503,"object_to_goal_dist_start":0.18207,"object_z_max":0.02193,"peak_contact_force":0.2959,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":162.0,"raw_peak_contact_force":0.39284,"tcp_end":[0.6181,0.15089,0.30513],"tcp_start":[0.61782,0.15112,0.23401],"tcp_to_object_dist_end":0.291,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```