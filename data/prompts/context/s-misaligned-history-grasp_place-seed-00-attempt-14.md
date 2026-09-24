## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 18  | -0.3652 | 0.33 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19  | -0.1287 | 0.76 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | -0.0249 | 0.95 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.0190 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 16  | -0.1302 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.130) — your mutation base

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

- **Composite score**: -0.130
- **task_score** (E): 0.800
- **fitness_score**: 0.870  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1131 |
| descend_to_grasp | 1.00 | 1.00 | 0.1420 |
| grasp_action | 1.00 | 1.00 | 0.0117 |
| lift_object | 0.33 | 1.00 | 0.1202 |
| transport_to_goal | 0.67 | 0.67 | 0.1834 |
| place_at_goal | 1.00 | 1.00 | 0.0369 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.003, 0.191) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.499, 0.003, 0.191)→(0.493, 0.001, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.493, 0.001, 0.049)→(0.485, 0.001, 0.041) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 45.667 | 0.153 | 0.221 |
| lift_object | lift | 0.33 / step_budget | (0.485, 0.001, 0.041)→(0.484, 0.001, 0.161) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.144) | 0.266→0.213 | 1.00 / 37.333 | 0.086 | 0.494 |
| transport_to_goal | approach | 0.67 / step_budget | (0.484, 0.001, 0.161)→(0.562, 0.148, 0.225) | (0.497, 0.001, 0.144)→(0.582, 0.150, 0.179) | 0.213→0.051 | 0.67 / 19.333 | 206.798 | 0.235 |
| place_at_goal | descend | 1.00 / step_budget | (0.562, 0.148, 0.225)→(0.581, 0.177, 0.216) | (0.582, 0.150, 0.179)→(0.594, 0.184, 0.142) | 0.051→0.055 | 1.00 / 23.667 | 91091.784 | 0.769 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.181
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.417
- phase_breakdown.grasp_target_score: 0.773
- phase_breakdown.pre_grasp_score: 0.166
- phase_breakdown.transport_goal_score: 0.243
- phase_breakdown.lift_target_score: 0.313
- phase_breakdown.final_place_score: 0.527
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.036
- **K-run variance**: 0.0193
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53086,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05168,"approach_object.approach_speed":0.11754,"approach_object.approach_tolerance":0.06853,"descend_to_grasp.descend_speed":0.15875,"descend_to_grasp.descend_tolerance":0.01003,"descend_to_grasp.grasp_offset_z":0.01945,"grasp_action.grasp_max_width":0.0287,"lift_object.lift_height":0.16044,"lift_object.lift_speed":0.05332,"lift_object.lift_tolerance":0.02578,"place_at_goal.place_offset_x":0.0051,"place_at_goal.place_offset_y":-0.00152,"place_at_goal.place_offset_z":0.03539,"place_at_goal.place_speed":0.07785,"place_at_goal.place_tolerance":0.00985,"transport_to_goal.transport_offset_z":0.0687,"transport_to_goal.transport_speed":0.21525,"transport_to_goal.transport_tolerance":0.04121},"optimized_scores":{"best_composite_score":-0.03593,"best_fitness_score":0.96407,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.51108,-0.02157,-0.0016],"force_p95":0.40411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44504,"mean_force":0.16061,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49976,-0.02166,0.04604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6319.0,"contact_point_centroid":[0.49757,-0.00237,0.11269],"force_p95":0.08264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29003,"mean_force":0.05897,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49754,-0.02159,0.1102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7462.0,"contact_point_centroid":[0.49757,-0.0407,0.11092],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28596,"mean_force":0.05199,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49755,-0.02159,0.10877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1925.0,"contact_point_centroid":[0.55312,0.1528,0.25624],"force_p95":0.13052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25109,"mean_force":0.09157,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.54864,0.13415,0.25721]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02292,-0.00212],"force_p95":0.15496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21486,"mean_force":0.13146,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50198,-0.02172,0.04628]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.55366,0.11563,0.25709],"force_p95":0.10052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19549,"mean_force":0.07716,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.54856,0.13401,0.25728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3315.0,"contact_point_centroid":[0.51963,0.02056,0.21634],"force_p95":0.11998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17993,"mean_force":0.06928,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51672,0.03941,0.21522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3020.0,"contact_point_centroid":[0.51991,0.05885,0.21648],"force_p95":0.1196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17016,"mean_force":0.07381,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51687,0.0399,0.21551]},{"body_a":"world","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.5137,-0.02302,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12376,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50627,-0.00686,0.23095]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50817,-0.01874,0.09521]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4581.0,"contact_point_centroid":[0.50158,-0.00244,0.04785],"force_p95":0.07244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11291,"mean_force":0.04729,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50082,-0.02169,0.045]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5462.0,"contact_point_centroid":[0.50102,-0.0409,0.0476],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07073,"mean_force":0.04078,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50083,-0.02169,0.045]}],"total_contact_groups":12},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56206,0.1441,0.22239],"final_tcp_position":[0.55354,0.14429,0.25186],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":269.16149,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.1224,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":436.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.51147,-0.01526,0.14851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12275,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_target","tcp_end":[0.5089,-0.02185,0.05406],"tcp_start":[0.51147,-0.01526,0.14851],"tcp_to_object_dist_end":0.02847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51365,-0.02209,0.02557],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26534,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15153,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11843.0,"raw_peak_contact_force":0.21486,"tcp_end":[0.50079,-0.02169,0.04497],"tcp_start":[0.5089,-0.02185,0.05406],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.50763,-0.02183,0.15801],"object_pos_start":[0.51365,-0.02209,0.02557],"object_to_goal_dist_end":0.19065,"object_to_goal_dist_start":0.26534,"object_z_max":0.15763,"peak_contact_force":0.08132,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13857.0,"raw_peak_contact_force":0.44504,"subtask_id":"lift_target","tcp_end":[0.49759,-0.02158,0.17999],"tcp_start":[0.50079,-0.02169,0.04497],"tcp_to_object_dist_end":0.02417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.55543,0.12104,0.23827],"object_pos_start":[0.50763,-0.02183,0.15801],"object_to_goal_dist_end":0.03469,"object_to_goal_dist_start":0.19065,"object_z_max":0.23792,"peak_contact_force":0.10951,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6335.0,"raw_peak_contact_force":0.17993,"subtask_id":"transport_goal","tcp_end":[0.54373,0.12124,0.26547],"tcp_start":[0.49759,-0.02158,0.17999],"tcp_to_object_dist_end":0.02962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.56206,0.1441,0.22239],"object_pos_start":[0.55543,0.12104,0.23827],"object_to_goal_dist_end":0.01099,"object_to_goal_dist_start":0.03469,"object_z_max":0.23881,"peak_contact_force":269.16149,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3977.0,"raw_peak_contact_force":0.25109,"subtask_id":"final_place","tcp_end":[0.55354,0.14429,0.25186],"tcp_start":[0.54373,0.12124,0.26547],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76552,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15378,"approach_object.approach_speed":0.19562,"approach_object.approach_tolerance":0.02445,"descend_to_grasp.descend_speed":0.10228,"descend_to_grasp.descend_tolerance":0.01043,"descend_to_grasp.grasp_offset_z":0.01081,"grasp_action.grasp_max_width":0.03634,"lift_object.lift_height":0.1575,"lift_object.lift_speed":0.09119,"lift_object.lift_tolerance":0.06569,"place_at_goal.place_offset_x":0.0183,"place_at_goal.place_offset_y":-0.012,"place_at_goal.place_offset_z":0.04167,"place_at_goal.place_speed":0.04774,"place_at_goal.place_tolerance":0.0123,"transport_to_goal.transport_offset_z":0.05262,"transport_to_goal.transport_speed":0.13495,"transport_to_goal.transport_tolerance":0.04495},"optimized_scores":{"best_composite_score":-0.32658,"best_fitness_score":0.67342,"best_task_score":0.4013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.60474,0.2495,-0.00298],"force_p95":0.51929,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59698,"mean_force":0.169,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.56498,0.22116,0.17796]},{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.49844,0.04336,-0.00166],"force_p95":0.51018,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53169,"mean_force":0.26131,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48702,0.04289,0.03838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1883.0,"contact_point_centroid":[0.48573,0.06192,0.07649],"force_p95":0.14525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31459,"mean_force":0.06732,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48547,0.04266,0.07452]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1711.0,"contact_point_centroid":[0.48583,0.02345,0.07573],"force_p95":0.14476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27921,"mean_force":0.07083,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48543,0.04266,0.073]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1799.0,"contact_point_centroid":[0.51077,0.07376,0.14859],"force_p95":0.15043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26915,"mean_force":0.09393,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50627,0.0925,0.14593]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04482,-0.00218],"force_p95":0.17093,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24372,"mean_force":0.13564,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48965,0.04314,0.03842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2214.0,"contact_point_centroid":[0.51351,0.11786,0.14923],"force_p95":0.13098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1981,"mean_force":0.08044,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5087,0.09933,0.14777]},{"body_a":"world","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.50118,0.04505,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12337,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49906,0.01628,0.25424]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49627,0.03901,0.12426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.48839,0.02378,0.04034],"force_p95":0.07187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12118,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48851,0.04303,0.0372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5561.0,"contact_point_centroid":[0.48821,0.06239,0.03973],"force_p95":0.07176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07634,"mean_force":0.04087,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48851,0.04303,0.03721]},{"body_a":"left_finger","body_b":"right_finger","contact_count":797.0,"contact_point_centroid":[0.56813,0.22311,0.18021],"force_p95":0.0129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01895,"mean_force":0.01095,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.56773,0.22308,0.17805]}],"total_contact_groups":12},"final_pose_error":0.01229,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.60489,0.24962,0.01602],"final_tcp_position":[0.57547,0.22869,0.17944],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273006.11039,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49855,0.03446,0.20514],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_target","tcp_end":[0.49654,0.04374,0.04587],"tcp_start":[0.49855,0.03446,0.20514],"tcp_to_object_dist_end":0.02042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.0435,0.02539],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24349,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16374,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12389.0,"raw_peak_contact_force":0.24372,"tcp_end":[0.48848,0.04303,0.03717],"tcp_start":[0.49654,0.04374,0.04587],"tcp_to_object_dist_end":0.0173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.50257,0.04295,0.11748],"object_pos_start":[0.50114,0.0435,0.02539],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.24349,"object_z_max":0.11626,"peak_contact_force":0.09182,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3659.0,"raw_peak_contact_force":0.53169,"subtask_id":"lift_target","tcp_end":[0.48715,0.04267,0.12956],"tcp_start":[0.48848,0.04303,0.03717],"tcp_to_object_dist_end":0.01959,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.58653,0.21374,0.09377],"object_pos_start":[0.50257,0.04295,0.11748],"object_to_goal_dist_end":0.06532,"object_to_goal_dist_start":0.2132,"object_z_max":0.14908,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4013.0,"raw_peak_contact_force":0.26915,"subtask_id":"transport_goal","tcp_end":[0.54898,0.20802,0.18008],"tcp_start":[0.48715,0.04267,0.12956],"tcp_to_object_dist_end":0.0943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.60489,0.24962,0.01602],"object_pos_start":[0.58653,0.21374,0.09377],"object_to_goal_dist_end":0.13696,"object_to_goal_dist_start":0.06532,"object_z_max":0.09377,"peak_contact_force":273006.11039,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1789.0,"raw_peak_contact_force":1.59698,"subtask_id":"final_place","tcp_end":[0.57547,0.22869,0.17944],"tcp_start":[0.54898,0.20802,0.18008],"tcp_to_object_dist_end":0.16737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95092,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13072,"approach_object.approach_speed":0.09795,"approach_object.approach_tolerance":0.06084,"descend_to_grasp.descend_speed":0.11867,"descend_to_grasp.descend_tolerance":0.01085,"descend_to_grasp.grasp_offset_z":0.01165,"grasp_action.grasp_max_width":0.04358,"lift_object.lift_height":0.20966,"lift_object.lift_speed":0.08413,"lift_object.lift_tolerance":0.07766,"place_at_goal.place_offset_x":-0.01323,"place_at_goal.place_offset_y":0.00261,"place_at_goal.place_offset_z":0.03508,"place_at_goal.place_speed":0.05332,"place_at_goal.place_tolerance":0.00528,"transport_to_goal.transport_offset_z":0.06203,"transport_to_goal.transport_speed":0.19578,"transport_to_goal.transport_tolerance":0.06298},"optimized_scores":{"best_composite_score":-0.02799,"best_fitness_score":0.97201,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.47427,-0.01924,-0.00156],"force_p95":0.46899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50609,"mean_force":0.22075,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46388,-0.01913,0.04083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18433.0,"contact_point_centroid":[0.60409,0.1589,0.21916],"force_p95":0.08114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45887,"mean_force":0.05377,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.60424,0.13973,0.21867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2208.0,"contact_point_centroid":[0.46342,-0.03827,0.09783],"force_p95":0.12508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29538,"mean_force":0.06458,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46328,-0.01906,0.09596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2110.0,"contact_point_centroid":[0.46329,0.00012,0.09569],"force_p95":0.12499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28918,"mean_force":0.06666,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46319,-0.01906,0.0935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2752.0,"contact_point_centroid":[0.52944,0.02429,0.20411],"force_p95":0.12863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25558,"mean_force":0.07518,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52839,0.04348,0.20183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20251.0,"contact_point_centroid":[0.60404,0.12042,0.21941],"force_p95":0.07414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25486,"mean_force":0.04852,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.60411,0.13945,0.21875]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02007,-0.00208],"force_p95":0.14714,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20387,"mean_force":0.1292,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46625,-0.01918,0.04086]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2921.0,"contact_point_centroid":[0.53201,0.0651,0.20472],"force_p95":0.10859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17137,"mean_force":0.06525,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53103,0.04629,0.20274]},{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.47616,-0.02015,-0.00155],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12461,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4955,-0.00474,0.2653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5110.0,"contact_point_centroid":[0.46479,3e-05,0.04125],"force_p95":0.06902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13844,"mean_force":0.04239,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46515,-0.01915,0.03976]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47908,-0.01532,0.12939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.46536,-0.03842,0.04163],"force_p95":0.07157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07608,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46516,-0.01915,0.03976]}],"total_contact_groups":12},"final_pose_error":0.01022,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61517,0.15836,0.18808],"final_tcp_position":[0.6136,0.15844,0.2166],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":620.28489,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02591],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28844,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12273,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":280.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48825,-0.01119,0.2184],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02591],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28844,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_target","tcp_end":[0.47288,-0.01931,0.04759],"tcp_start":[0.48825,-0.01119,0.2184],"tcp_to_object_dist_end":0.02184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01943,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14473,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11855.0,"raw_peak_contact_force":0.20387,"tcp_end":[0.46513,-0.01915,0.03973],"tcp_start":[0.47288,-0.01931,0.04759],"tcp_to_object_dist_end":0.01781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.4805,-0.01911,0.15774],"object_pos_start":[0.47608,-0.01943,0.02569],"object_to_goal_dist_end":0.23582,"object_to_goal_dist_start":0.28817,"object_z_max":0.1563,"peak_contact_force":0.08488,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4380.0,"raw_peak_contact_force":0.50609,"subtask_id":"lift_target","tcp_end":[0.46637,-0.01906,0.17274],"tcp_start":[0.46513,-0.01915,0.03973],"tcp_to_object_dist_end":0.0206,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.60395,0.11517,0.20598],"object_pos_start":[0.4805,-0.01911,0.15774],"object_to_goal_dist_end":0.05429,"object_to_goal_dist_start":0.23582,"object_z_max":0.20569,"peak_contact_force":620.28489,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5673.0,"raw_peak_contact_force":0.25558,"subtask_id":"transport_goal","tcp_end":[0.59475,0.1153,0.22842],"tcp_start":[0.46637,-0.01906,0.17274],"tcp_to_object_dist_end":0.02425,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61517,0.15836,0.18808],"object_pos_start":[0.60395,0.11517,0.20598],"object_to_goal_dist_end":0.01638,"object_to_goal_dist_start":0.05429,"object_z_max":0.20647,"peak_contact_force":0.08036,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":38684.0,"raw_peak_contact_force":0.45887,"subtask_id":"final_place","tcp_end":[0.6136,0.15844,0.2166],"tcp_start":[0.59475,0.1153,0.22842],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```