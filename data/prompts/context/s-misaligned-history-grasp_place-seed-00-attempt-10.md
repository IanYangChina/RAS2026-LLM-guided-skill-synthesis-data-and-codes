## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 16  | -0.0266 | 0.95 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1723 | 0.78 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12  | -0.3721 | 0.31 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17  | -0.0764 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | 0.0190 | 0.94 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.019) — your mutation base

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

- **Composite score**: 0.019
- **task_score** (E): 0.941
- **fitness_score**: 0.939  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.920

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.0746 |
| descend_to_grasp | 1.00 | 1.00 | 0.1799 |
| grasp_action | 1.00 | 1.00 | 0.0118 |
| lift_object | 0.33 | 1.00 | 0.1442 |
| transport_to_goal | 0.67 | 1.00 | 0.1707 |
| fine_placement | 1.00 | 1.00 | 0.0466 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.003, 0.229) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.128 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.494, -0.003, 0.229)→(0.492, 0.000, 0.050) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.128 |
| grasp_action | grasp | 1.00 / step_budget | (0.492, 0.000, 0.050)→(0.484, 0.000, 0.041) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 45.333 | 0.157 | 0.219 |
| lift_object | lift | 0.33 / step_budget | (0.484, 0.000, 0.041)→(0.484, 0.000, 0.185) | (0.497, 0.000, 0.025)→(0.502, 0.000, 0.168) | 0.266→0.209 | 1.00 / 27.667 | 0.113 | 0.499 |
| transport_to_goal | approach | 0.67 / step_budget | (0.484, 0.000, 0.185)→(0.564, 0.146, 0.180) | (0.502, 0.000, 0.168)→(0.577, 0.146, 0.159) | 0.209→0.050 | 1.00 / 30.000 | 0.115 | 0.295 |
| fine_placement | approach | 1.00 / step_budget | (0.564, 0.146, 0.180)→(0.581, 0.183, 0.201) | (0.577, 0.146, 0.159)→(0.592, 0.183, 0.176) | 0.050→0.016 | 1.00 / 25.000 | 0.135 | 0.408 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.536
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.618
- phase_breakdown.lift_score: 0.429
- phase_breakdown.place_score: 0.462
- phase_breakdown.pre_grasp_score: 0.555
- phase_breakdown.place_fine_score: 0.805
- phase_breakdown.grasp_score: 0.723
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.050
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85806,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.18083,"approach_object.approach_speed":0.1114,"approach_object.approach_tolerance":0.05829,"descend_to_grasp.descend_speed":0.11138,"descend_to_grasp.descend_tolerance":0.01441,"descend_to_grasp.grasp_offset_z":0.01471,"fine_placement.place_offset_x":0.0091,"fine_placement.place_offset_y":0.00503,"fine_placement.place_offset_z":0.01249,"fine_placement.place_speed":0.0649,"fine_placement.place_tolerance":0.01346,"lift_object.lift_height":0.2022,"lift_object.lift_speed":0.08982,"lift_object.lift_tolerance":0.04351,"transport_to_goal.transport_speed":0.15175,"transport_to_goal.transport_tolerance":0.04301},"optimized_scores":{"best_composite_score":-0.04479,"best_fitness_score":0.87521,"best_task_score":0.8226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.5117,-0.0217,-0.00162],"force_p95":0.41121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43237,"mean_force":0.16673,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49926,-0.02147,0.04606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3510.0,"contact_point_centroid":[0.55468,0.15206,0.21734],"force_p95":0.0972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41592,"mean_force":0.07536,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54859,0.1333,0.21706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3445.0,"contact_point_centroid":[0.55489,0.11423,0.21725],"force_p95":0.10032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32469,"mean_force":0.07549,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54841,0.13293,0.2169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3398.0,"contact_point_centroid":[0.50038,-0.00234,0.11261],"force_p95":0.12482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29557,"mean_force":0.0753,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49791,-0.02141,0.11014]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3790.0,"contact_point_centroid":[0.49998,-0.04043,0.1119],"force_p95":0.11973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28609,"mean_force":0.06967,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49791,-0.02142,0.10963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.52447,0.0238,0.20919],"force_p95":0.13389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24548,"mean_force":0.09333,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51865,0.04248,0.20768]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51374,-0.02291,-0.00213],"force_p95":0.15871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21875,"mean_force":0.13241,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50179,-0.02153,0.04622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2053.0,"contact_point_centroid":[0.5254,0.06416,0.209],"force_p95":0.11351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1487,"mean_force":0.08167,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51961,0.04567,0.20777]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.5137,-0.02302,-0.00108],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12245,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50288,-0.00293,0.28777]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.5137,-0.02302,-0.002],"force_p95":0.1241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1336,"mean_force":0.12289,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50651,-0.01491,0.15673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4578.0,"contact_point_centroid":[0.50155,-0.00226,0.04778],"force_p95":0.07251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11551,"mean_force":0.04729,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50064,-0.0215,0.04495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.50084,-0.04072,0.04759],"force_p95":0.06844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07175,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50064,-0.0215,0.04496]}],"total_contact_groups":12},"final_pose_error":0.01338,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56729,0.15014,0.19588],"final_tcp_position":[0.55711,0.15025,0.22445],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.43237,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02615],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26551,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.13411,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":144.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50629,-0.00792,0.26646],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02615],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26551,"object_z_max":0.02615,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.1336,"subtask_id":"grasp","tcp_end":[0.50884,-0.02165,0.05421],"tcp_start":[0.50629,-0.00792,0.26646],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51366,-0.02197,0.02552],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26529,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15484,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11860.0,"raw_peak_contact_force":0.21875,"tcp_end":[0.50061,-0.0215,0.04492],"tcp_start":[0.50884,-0.02165,0.05421],"tcp_to_object_dist_end":0.02338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.51801,-0.02181,0.18265],"object_pos_start":[0.51366,-0.02197,0.02552],"object_to_goal_dist_end":0.18149,"object_to_goal_dist_start":0.26529,"object_z_max":0.18191,"peak_contact_force":0.11574,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7253.0,"raw_peak_contact_force":0.43237,"subtask_id":"lift","tcp_end":[0.49861,-0.02141,0.20433],"tcp_start":[0.50061,-0.0215,0.04492],"tcp_to_object_dist_end":0.0291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.5562,0.112,0.18689],"object_pos_start":[0.51801,-0.02181,0.18265],"object_to_goal_dist_end":0.053,"object_to_goal_dist_start":0.18149,"object_z_max":0.18684,"peak_contact_force":0.09929,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3965.0,"raw_peak_contact_force":0.24548,"subtask_id":"place","tcp_end":[0.54043,0.11237,0.21202],"tcp_start":[0.49861,-0.02141,0.20433],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.56729,0.15014,0.19588],"object_pos_start":[0.5562,0.112,0.18689],"object_to_goal_dist_end":0.02929,"object_to_goal_dist_start":0.053,"object_z_max":0.19585,"peak_contact_force":0.14445,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6955.0,"raw_peak_contact_force":0.41592,"subtask_id":"place_fine","tcp_end":[0.55711,0.15025,0.22445],"tcp_start":[0.54043,0.11237,0.21202],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6646,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.17908,"approach_object.approach_speed":0.04847,"approach_object.approach_tolerance":0.05968,"descend_to_grasp.descend_speed":0.12732,"descend_to_grasp.descend_tolerance":0.01163,"descend_to_grasp.grasp_offset_z":0.01192,"fine_placement.place_offset_x":-0.00208,"fine_placement.place_offset_y":0.00201,"fine_placement.place_offset_z":0.03585,"fine_placement.place_speed":0.07303,"fine_placement.place_tolerance":0.01773,"lift_object.lift_height":0.1792,"lift_object.lift_speed":0.13282,"lift_object.lift_tolerance":0.05626,"transport_to_goal.transport_speed":0.14497,"transport_to_goal.transport_tolerance":0.05358},"optimized_scores":{"best_composite_score":0.0502,"best_fitness_score":0.9702,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.49778,0.04241,-0.00179],"force_p95":0.53469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5842,"mean_force":0.26755,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48683,0.04188,0.04074]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2511.0,"contact_point_centroid":[0.55566,0.23573,0.1559],"force_p95":0.11921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45412,"mean_force":0.09107,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54995,0.21744,0.15529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.48691,0.06088,0.09384],"force_p95":0.14092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36084,"mean_force":0.06928,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48595,0.0417,0.09177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1866.0,"contact_point_centroid":[0.55518,0.19893,0.15805],"force_p95":0.16258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35773,"mean_force":0.11137,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54999,0.2175,0.15537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2262.0,"contact_point_centroid":[0.48699,0.02251,0.09338],"force_p95":0.14933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31919,"mean_force":0.07386,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48593,0.0417,0.09062]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.52083,0.0948,0.15765],"force_p95":0.14511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29754,"mean_force":0.09603,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51594,0.11365,0.1553]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50128,0.04477,-0.00225],"force_p95":0.19162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25954,"mean_force":0.14089,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48992,0.04215,0.0408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1946.0,"contact_point_centroid":[0.5211,0.13226,0.15662],"force_p95":0.12165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17555,"mean_force":0.08594,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.516,0.11382,0.15528]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.50118,0.04505,-0.00134],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12467,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50028,0.00596,0.28667]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4783.0,"contact_point_centroid":[0.4889,0.02281,0.04247],"force_p95":0.07572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13635,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48878,0.04205,0.03958]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12703,"mean_force":0.12266,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49779,0.03025,0.15124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5407.0,"contact_point_centroid":[0.48872,0.06146,0.04188],"force_p95":0.07679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08175,"mean_force":0.04246,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4888,0.04205,0.03959]}],"total_contact_groups":12},"final_pose_error":0.01767,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5701,0.2375,0.1469],"final_tcp_position":[0.55619,0.23738,0.16905],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.5842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":51.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02587],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24196,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12742,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":200.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50116,0.01743,0.2614],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23715,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02587],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24196,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.12703,"subtask_id":"grasp","tcp_end":[0.4968,0.04271,0.04828],"tcp_start":[0.50116,0.01743,0.2614],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04284,0.02513],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24415,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.18143,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11990.0,"raw_peak_contact_force":0.25954,"tcp_end":[0.48876,0.04204,0.03955],"tcp_start":[0.4968,0.04271,0.04828],"tcp_to_object_dist_end":0.01904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":129.0,"n_steps_budget":840.0,"object_pos_end":[0.5057,0.04223,0.14756],"object_pos_start":[0.50116,0.04284,0.02513],"object_to_goal_dist_end":0.21097,"object_to_goal_dist_start":0.24415,"object_z_max":0.14654,"peak_contact_force":0.11375,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4865.0,"raw_peak_contact_force":0.5842,"subtask_id":"lift","tcp_end":[0.48789,0.04176,0.16258],"tcp_start":[0.48876,0.04204,0.03955],"tcp_to_object_dist_end":0.0233,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.5631,0.1956,0.12732],"object_pos_start":[0.5057,0.04223,0.14756],"object_to_goal_dist_end":0.05299,"object_to_goal_dist_start":0.21097,"object_z_max":0.15286,"peak_contact_force":0.11173,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3734.0,"raw_peak_contact_force":0.29754,"subtask_id":"place","tcp_end":[0.54585,0.19526,0.14484],"tcp_start":[0.48789,0.04176,0.16258],"tcp_to_object_dist_end":0.02459,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.5701,0.2375,0.1469],"object_pos_start":[0.5631,0.1956,0.12732],"object_to_goal_dist_end":0.0093,"object_to_goal_dist_start":0.05299,"object_z_max":0.14681,"peak_contact_force":0.16773,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4377.0,"raw_peak_contact_force":0.45412,"subtask_id":"place_fine","tcp_end":[0.55619,0.23738,0.16905],"tcp_start":[0.54585,0.19526,0.14484],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11718,"approach_object.approach_speed":0.16386,"approach_object.approach_tolerance":0.01243,"descend_to_grasp.descend_speed":0.14561,"descend_to_grasp.descend_tolerance":0.01188,"descend_to_grasp.grasp_offset_z":0.01008,"fine_placement.place_offset_x":0.00649,"fine_placement.place_offset_y":0.00646,"fine_placement.place_offset_z":0.03396,"fine_placement.place_speed":0.07218,"fine_placement.place_tolerance":0.01639,"lift_object.lift_height":0.21169,"lift_object.lift_speed":0.0828,"lift_object.lift_tolerance":0.06254,"transport_to_goal.transport_speed":0.14054,"transport_to_goal.transport_tolerance":0.03906},"optimized_scores":{"best_composite_score":0.05167,"best_fitness_score":0.97167,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":61.0,"contact_point_centroid":[0.47389,-0.01959,-0.00152],"force_p95":0.47236,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47907,"mean_force":0.21928,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46289,-0.01954,0.04033]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5931.0,"contact_point_centroid":[0.61942,0.16613,0.19734],"force_p95":0.07553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35297,"mean_force":0.04879,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.61766,0.14718,0.19535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.54276,0.04158,0.18842],"force_p95":0.13966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34331,"mean_force":0.09055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53888,0.06038,0.1866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5180.0,"contact_point_centroid":[0.62007,0.12784,0.19701],"force_p95":0.09027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31538,"mean_force":0.0603,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.61743,0.14694,0.19509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2656.0,"contact_point_centroid":[0.46279,-0.00029,0.10512],"force_p95":0.11378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2819,"mean_force":0.06715,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46219,-0.01947,0.10262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2874.0,"contact_point_centroid":[0.46287,-0.03862,0.10548],"force_p95":0.11282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28025,"mean_force":0.06338,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46222,-0.01947,0.1036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3687.0,"contact_point_centroid":[0.54386,0.07997,0.18783],"force_p95":0.12269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23005,"mean_force":0.07762,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53993,0.06152,0.18651]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02008,-0.00205],"force_p95":0.1378,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17887,"mean_force":0.12679,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46518,-0.01959,0.04039]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48732,-0.00858,0.23054]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47249,-0.01871,0.10301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5077.0,"contact_point_centroid":[0.46377,-0.00033,0.04186],"force_p95":0.06607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10428,"mean_force":0.04288,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01956,0.03929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5202.0,"contact_point_centroid":[0.46393,-0.03881,0.04129],"force_p95":0.06654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0844,"mean_force":0.04259,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46409,-0.01956,0.03929]}],"total_contact_groups":12},"final_pose_error":0.01629,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63974,0.161,0.18631],"final_tcp_position":[0.6307,0.16072,0.21023],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.47907,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47542,-0.01778,0.15934],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp","tcp_end":[0.47184,-0.01974,0.04715],"tcp_start":[0.47542,-0.01778,0.15934],"tcp_to_object_dist_end":0.02157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01969,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13593,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12079.0,"raw_peak_contact_force":0.17887,"tcp_end":[0.46406,-0.01956,0.03926],"tcp_start":[0.47184,-0.01974,0.04715],"tcp_to_object_dist_end":0.01804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.48113,-0.01941,0.17485],"object_pos_start":[0.47607,-0.01969,0.0258],"object_to_goal_dist_end":0.23392,"object_to_goal_dist_start":0.28827,"object_z_max":0.17372,"peak_contact_force":0.11073,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5591.0,"raw_peak_contact_force":0.47907,"subtask_id":"lift","tcp_end":[0.46404,-0.01946,0.18947],"tcp_start":[0.46406,-0.01956,0.03926],"tcp_to_object_dist_end":0.02248,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.61276,0.1307,0.16169],"object_pos_start":[0.48113,-0.01941,0.17485],"object_to_goal_dist_end":0.0443,"object_to_goal_dist_start":0.23392,"object_z_max":0.18191,"peak_contact_force":0.13442,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7083.0,"raw_peak_contact_force":0.34331,"subtask_id":"place","tcp_end":[0.60517,0.13164,0.18364],"tcp_start":[0.46404,-0.01946,0.18947],"tcp_to_object_dist_end":0.02324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.63974,0.161,0.18631],"object_pos_start":[0.61276,0.1307,0.16169],"object_to_goal_dist_end":0.00929,"object_to_goal_dist_start":0.0443,"object_z_max":0.18624,"peak_contact_force":0.09175,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11111.0,"raw_peak_contact_force":0.35297,"subtask_id":"place_fine","tcp_end":[0.6307,0.16072,0.21023],"tcp_start":[0.60517,0.13164,0.18364],"tcp_to_object_dist_end":0.02557,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```