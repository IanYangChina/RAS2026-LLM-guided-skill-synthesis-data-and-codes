## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | -0.0249 | 0.95 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.0190 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 16  | -0.0266 | 0.95 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1723 | 0.78 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12  | -0.1287 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.129) — your mutation base

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

- **Composite score**: -0.129
- **task_score** (E): 0.760
- **fitness_score**: 0.841  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.970

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.0525 |
| descend_to_grasp | 1.00 | 1.00 | 0.1943 |
| grasp_action | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1235 |
| transport_to_goal | 1.00 | 1.00 | 0.1927 |
| fine_placement | 1.00 | 1.00 | 0.0230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.001, 0.250) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 28.989 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.503, -0.001, 0.250)→(0.494, -0.000, 0.057) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.131 |
| grasp_action | grasp | 1.00 / step_budget | (0.494, -0.000, 0.057)→(0.485, -0.000, 0.048) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 42.000 | 0.185 | 0.236 |
| lift_object | lift | 1.00 / step_budget | (0.485, -0.000, 0.048)→(0.484, -0.000, 0.171) | (0.497, 0.000, 0.025)→(0.500, 0.000, 0.147) | 0.266→0.215 | 1.00 / 30.333 | 0.123 | 0.457 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, -0.000, 0.171)→(0.570, 0.164, 0.179) | (0.500, 0.000, 0.147)→(0.575, 0.164, 0.147) | 0.215→0.047 | 1.00 / 20.667 | 0.129 | 0.260 |
| fine_placement | approach | 1.00 / step_budget | (0.570, 0.164, 0.179)→(0.579, 0.179, 0.182) | (0.575, 0.164, 0.147)→(0.583, 0.179, 0.147) | 0.047→0.041 | 1.00 / 18.000 | 0.126 | 0.408 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.789
- phase_score: 0.485
- phase_breakdown.lift_score: 0.272
- phase_breakdown.place_score: 0.610
- phase_breakdown.pre_grasp_score: 0.074
- phase_breakdown.place_fine_score: 0.626
- phase_breakdown.grasp_score: 0.795
- grasp_place_fitness: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.860
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.789
- **Median Q (composite search score)**: -0.129
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86301,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14682,"approach_object.approach_speed":0.11199,"approach_object.approach_tolerance":0.06838,"descend_to_grasp.descend_speed":0.16404,"descend_to_grasp.descend_tolerance":0.0122,"descend_to_grasp.grasp_offset_z":0.0213,"fine_placement.place_offset_x":-0.01497,"fine_placement.place_offset_y":0.0085,"fine_placement.place_offset_z":-0.00348,"fine_placement.place_speed":0.04522,"fine_placement.place_tolerance":0.01011,"grasp_action.grasp_max_width":0.04519,"lift_object.lift_height":0.16073,"lift_object.lift_speed":0.10585,"lift_object.lift_tolerance":0.04073,"transport_to_goal.transport_speed":0.08752,"transport_to_goal.transport_tolerance":0.01836},"optimized_scores":{"best_composite_score":-0.1475,"best_fitness_score":0.8225,"best_task_score":0.7269},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.51143,-0.02212,-0.0016],"force_p95":0.36726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38586,"mean_force":0.1391,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4992,-0.0216,0.05018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2786.0,"contact_point_centroid":[0.4998,-0.0025,0.10045],"force_p95":0.13635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28656,"mean_force":0.07763,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49783,-0.02155,0.10001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3020.0,"contact_point_centroid":[0.49973,-0.04055,0.09994],"force_p95":0.12778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27911,"mean_force":0.07253,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49783,-0.02155,0.09929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.54669,0.1285,0.20651],"force_p95":0.13742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24439,"mean_force":0.11265,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54175,0.14667,0.20983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1125.0,"contact_point_centroid":[0.54658,0.16526,0.20665],"force_p95":0.13359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22318,"mean_force":0.1033,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54145,0.14717,0.20979]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6530.0,"contact_point_centroid":[0.52619,0.03988,0.18778],"force_p95":0.12063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22277,"mean_force":0.07995,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52111,0.05797,0.18826]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51374,-0.02295,-0.00212],"force_p95":0.15524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21167,"mean_force":0.13122,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50188,-0.02166,0.05038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5339.0,"contact_point_centroid":[0.52498,0.07386,0.18542],"force_p95":0.1369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19475,"mean_force":0.09936,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52032,0.05533,0.1876]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.5137,-0.02302,-0.00131],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12455,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50401,-0.00391,0.27732]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4339.0,"contact_point_centroid":[0.50121,-0.00244,0.0498],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1291,"mean_force":0.04954,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50073,-0.02163,0.0491]},{"body_a":"world","body_b":"grasp_target","contact_count":1716.0,"contact_point_centroid":[0.5137,-0.02302,-0.002],"force_p95":0.12273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12782,"mean_force":0.1227,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50734,-0.01606,0.14516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4978.0,"contact_point_centroid":[0.50119,-0.0408,0.04984],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07391,"mean_force":0.04419,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50074,-0.02163,0.04911]}],"total_contact_groups":12},"final_pose_error":0.01007,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54272,0.15305,0.17554],"final_tcp_position":[0.53775,0.15435,0.2104],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.38586,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":49.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02589],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26571,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12823,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":192.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50829,-0.00992,0.24272],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2173,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02589],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26571,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.12782,"subtask_id":"grasp","tcp_end":[0.50884,-0.02179,0.05828],"tcp_start":[0.50829,-0.00992,0.24272],"tcp_to_object_dist_end":0.03265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51365,-0.02211,0.02558],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26534,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15266,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11117.0,"raw_peak_contact_force":0.21167,"tcp_end":[0.5007,-0.02163,0.04907],"tcp_start":[0.50884,-0.02179,0.05828],"tcp_to_object_dist_end":0.02683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":173.0,"n_steps_budget":960.0,"object_pos_end":[0.51511,-0.02206,0.14343],"object_pos_start":[0.51365,-0.02211,0.02558],"object_to_goal_dist_end":0.1946,"object_to_goal_dist_start":0.26534,"object_z_max":0.14275,"peak_contact_force":0.13805,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5870.0,"raw_peak_contact_force":0.38586,"subtask_id":"lift","tcp_end":[0.49834,-0.02154,0.16924],"tcp_start":[0.5007,-0.02163,0.04907],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.55243,0.13703,0.17765],"object_pos_start":[0.51511,-0.02206,0.14343],"object_to_goal_dist_end":0.04672,"object_to_goal_dist_start":0.1946,"object_z_max":0.1776,"peak_contact_force":0.12659,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11869.0,"raw_peak_contact_force":0.22277,"subtask_id":"place","tcp_end":[0.54701,0.13875,0.21142],"tcp_start":[0.49834,-0.02154,0.16924],"tcp_to_object_dist_end":0.03425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.54272,0.15305,0.17554],"object_pos_start":[0.55243,0.13703,0.17765],"object_to_goal_dist_end":0.04784,"object_to_goal_dist_start":0.04672,"object_z_max":0.17765,"peak_contact_force":0.12547,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2169.0,"raw_peak_contact_force":0.24439,"subtask_id":"place_fine","tcp_end":[0.53775,0.15435,0.2104],"tcp_start":[0.54701,0.13875,0.21142],"tcp_to_object_dist_end":0.03524,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80435,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12583,"approach_object.approach_speed":0.08356,"approach_object.approach_tolerance":0.09858,"descend_to_grasp.descend_speed":0.0792,"descend_to_grasp.descend_tolerance":0.02413,"descend_to_grasp.grasp_offset_z":0.01001,"fine_placement.place_offset_x":0.00447,"fine_placement.place_offset_y":-0.01003,"fine_placement.place_offset_z":0.0078,"fine_placement.place_speed":0.07401,"fine_placement.place_tolerance":0.00993,"grasp_action.grasp_max_width":0.04074,"lift_object.lift_height":0.17729,"lift_object.lift_speed":0.12154,"lift_object.lift_tolerance":0.04853,"transport_to_goal.transport_speed":0.11878,"transport_to_goal.transport_tolerance":0.03827},"optimized_scores":{"best_composite_score":-0.1291,"best_fitness_score":0.8409,"best_task_score":0.76553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":6692.0,"contact_point_centroid":[0.5612,0.24079,0.14112],"force_p95":0.13701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52422,"mean_force":0.09266,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.55678,0.22264,0.1435]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49858,0.04108,-0.00193],"force_p95":0.4967,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51604,"mean_force":0.18098,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48772,0.03989,0.05097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5698.0,"contact_point_centroid":[0.56267,0.20584,0.14023],"force_p95":0.14215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36198,"mean_force":0.10464,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.55794,0.22415,0.14391]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2086.0,"contact_point_centroid":[0.52353,0.10669,0.1588],"force_p95":0.15897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31695,"mean_force":0.11615,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51899,0.12526,0.16152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1910.0,"contact_point_centroid":[0.48865,0.02069,0.10259],"force_p95":0.16528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31332,"mean_force":0.09704,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48696,0.03974,0.10452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3048.0,"contact_point_centroid":[0.48767,0.0583,0.1076],"force_p95":0.13802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3059,"mean_force":0.07105,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48698,0.03973,0.10704]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50133,0.0448,-0.00235],"force_p95":0.26695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2816,"mean_force":0.17831,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49062,0.04014,0.05076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3140.0,"contact_point_centroid":[0.52265,0.1413,0.1615],"force_p95":0.12855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20305,"mean_force":0.08068,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51827,0.12325,0.16192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3618.0,"contact_point_centroid":[0.48997,0.02089,0.04816],"force_p95":0.10558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14639,"mean_force":0.06834,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48952,0.04004,0.04958]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.50118,0.04505,-0.00121],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12386,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50192,0.00499,0.28317]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.50118,0.04505,-0.002],"force_p95":0.12508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13053,"mean_force":0.12287,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50012,0.02836,0.1466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5421.0,"contact_point_centroid":[0.48911,0.05922,0.04989],"force_p95":0.08461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10135,"mean_force":0.04953,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48954,0.04004,0.0496]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56936,0.23335,0.1087],"final_tcp_position":[0.5641,0.23215,0.14627],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":86.70356,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02597],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24191,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":86.70356,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":168.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50494,0.01505,0.24879],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22486,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02597],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24191,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13053,"subtask_id":"grasp","tcp_end":[0.49795,0.04064,0.05922],"tcp_start":[0.50494,0.01505,0.24879],"tcp_to_object_dist_end":0.03364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50123,0.04175,0.02475],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24523,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.2518,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.2816,"tcp_end":[0.4895,0.04004,0.04955],"tcp_start":[0.49795,0.04064,0.05922],"tcp_to_object_dist_end":0.02749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":155.0,"n_steps_budget":930.0,"object_pos_end":[0.50368,0.04147,0.15207],"object_pos_start":[0.50123,0.04175,0.02475],"object_to_goal_dist_end":0.21234,"object_to_goal_dist_start":0.24523,"object_z_max":0.15122,"peak_contact_force":0.14684,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5024.0,"raw_peak_contact_force":0.51604,"subtask_id":"lift","tcp_end":[0.4881,0.03977,0.17885],"tcp_start":[0.4895,0.04004,0.04955],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.55826,0.21169,0.11486],"object_pos_start":[0.50368,0.04147,0.15207],"object_to_goal_dist_end":0.04644,"object_to_goal_dist_start":0.21234,"object_z_max":0.15526,"peak_contact_force":0.13894,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5226.0,"raw_peak_contact_force":0.31695,"subtask_id":"place","tcp_end":[0.54962,0.20976,0.1454],"tcp_start":[0.4881,0.03977,0.17885],"tcp_to_object_dist_end":0.0318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.56936,0.23335,0.1087],"object_pos_start":[0.55826,0.21169,0.11486],"object_to_goal_dist_end":0.04008,"object_to_goal_dist_start":0.04644,"object_z_max":0.11486,"peak_contact_force":0.13729,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12390.0,"raw_peak_contact_force":0.52422,"subtask_id":"place_fine","tcp_end":[0.5641,0.23215,0.14627],"tcp_start":[0.54962,0.20976,0.1454],"tcp_to_object_dist_end":0.03795,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98101,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15195,"approach_object.approach_speed":0.1078,"approach_object.approach_tolerance":0.08021,"descend_to_grasp.descend_speed":0.08408,"descend_to_grasp.descend_tolerance":0.01403,"descend_to_grasp.grasp_offset_z":0.01317,"fine_placement.place_offset_x":0.01483,"fine_placement.place_offset_y":-0.00727,"fine_placement.place_offset_z":0.0127,"fine_placement.place_speed":0.10559,"fine_placement.place_tolerance":0.01687,"grasp_action.grasp_max_width":0.03273,"lift_object.lift_height":0.17022,"lift_object.lift_speed":0.13211,"lift_object.lift_tolerance":0.04984,"transport_to_goal.transport_speed":0.15761,"transport_to_goal.transport_tolerance":0.02506},"optimized_scores":{"best_composite_score":-0.10953,"best_fitness_score":0.86047,"best_task_score":0.78873},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.47298,-0.01891,-0.0016],"force_p95":0.42991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4705,"mean_force":0.20265,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46421,-0.01874,0.04612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1859.0,"contact_point_centroid":[0.62502,0.16525,0.18015],"force_p95":0.10659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45523,"mean_force":0.07748,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.62591,0.14692,0.18382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2624.0,"contact_point_centroid":[0.46409,0.00056,0.10403],"force_p95":0.11771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35801,"mean_force":0.06849,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46358,-0.0187,0.10109]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3038.0,"contact_point_centroid":[0.46384,-0.03782,0.10183],"force_p95":0.11135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31953,"mean_force":0.062,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46357,-0.0187,0.09966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1438.0,"contact_point_centroid":[0.62296,0.12824,0.18093],"force_p95":0.12081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31695,"mean_force":0.09577,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.6261,0.14697,0.18392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7647.0,"contact_point_centroid":[0.53379,0.03651,0.17249],"force_p95":0.11934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23999,"mean_force":0.07092,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53253,0.05535,0.17156]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.01998,-0.00212],"force_p95":0.15594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.215,"mean_force":0.13172,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4671,-0.01881,0.04606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7546.0,"contact_point_centroid":[0.53741,0.07823,0.1723],"force_p95":0.11443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21287,"mean_force":0.06564,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53639,0.05953,0.17193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.46685,0.00051,0.04834],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13853,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46602,-0.01878,0.04497]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47616,-0.02015,-0.00106],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12212,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49851,-0.00235,0.2856]},{"body_a":"world","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13411,"mean_force":0.12292,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48276,-0.01303,0.15019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5471.0,"contact_point_centroid":[0.46587,-0.03788,0.04764],"force_p95":0.06742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07114,"mean_force":0.04066,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46603,-0.01878,0.04497]}],"total_contact_groups":12},"final_pose_error":0.01678,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63555,0.1495,0.15601],"final_tcp_position":[0.63636,0.14935,0.18941],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.4705,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":36.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02619],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.13462,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":140.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49488,-0.00675,0.25823],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23317,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02619],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28828,"object_z_max":0.02619,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.13411,"subtask_id":"grasp","tcp_end":[0.4738,-0.01892,0.053],"tcp_start":[0.49488,-0.00675,0.25823],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47611,-0.01903,0.02556],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28798,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15067,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11364.0,"raw_peak_contact_force":0.215,"tcp_end":[0.46599,-0.01878,0.04494],"tcp_start":[0.4738,-0.01892,0.053],"tcp_to_object_dist_end":0.02186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":140.0,"n_steps_budget":810.0,"object_pos_end":[0.48102,-0.01906,0.14607],"object_pos_start":[0.47611,-0.01903,0.02556],"object_to_goal_dist_end":0.23733,"object_to_goal_dist_start":0.28798,"object_z_max":0.14517,"peak_contact_force":0.08308,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5724.0,"raw_peak_contact_force":0.4705,"subtask_id":"lift","tcp_end":[0.46495,-0.01869,0.16593],"tcp_start":[0.46599,-0.01878,0.04494],"tcp_to_object_dist_end":0.02555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.61506,0.14353,0.14786],"object_pos_start":[0.48102,-0.01906,0.14607],"object_to_goal_dist_end":0.04785,"object_to_goal_dist_start":0.23733,"object_z_max":0.15022,"peak_contact_force":0.12069,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15193.0,"raw_peak_contact_force":0.23999,"subtask_id":"place","tcp_end":[0.61483,0.14364,0.18036],"tcp_start":[0.46495,-0.01869,0.16593],"tcp_to_object_dist_end":0.0325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.63555,0.1495,0.15601],"object_pos_start":[0.61506,0.14353,0.14786],"object_to_goal_dist_end":0.0356,"object_to_goal_dist_start":0.04785,"object_z_max":0.15594,"peak_contact_force":0.11598,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3297.0,"raw_peak_contact_force":0.45523,"subtask_id":"place_fine","tcp_end":[0.63636,0.14935,0.18941],"tcp_start":[0.61483,0.14364,0.18036],"tcp_to_object_dist_end":0.03341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```