## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1723 | 0.78 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12  | -0.3721 | 0.31 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17  | -0.0764 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | -0.1713 | 0.18 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.0266 | 0.95 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=-0.027) — your mutation base

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

- **Composite score**: -0.027
- **task_score** (E): 0.954
- **fitness_score**: 0.943  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.970

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1043 |
| descend_to_grasp | 1.00 | 1.00 | 0.1477 |
| grasp_action | 1.00 | 1.00 | 0.0118 |
| lift_object | 0.33 | 1.00 | 0.1178 |
| transport_to_goal | 0.67 | 1.00 | 0.1712 |
| fine_placement | 1.00 | 1.00 | 0.0528 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.002, 0.199) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.497, -0.002, 0.199)→(0.493, 0.001, 0.052) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.493, 0.001, 0.052)→(0.485, 0.000, 0.043) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.667 | 0.156 | 0.220 |
| lift_object | lift | 0.33 / step_budget | (0.485, 0.000, 0.043)→(0.484, 0.000, 0.161) | (0.497, 0.001, 0.026)→(0.498, 0.001, 0.142) | 0.266→0.215 | 1.00 / 33.000 | 25.642 | 0.455 |
| transport_to_goal | approach | 0.67 / step_budget | (0.484, 0.000, 0.161)→(0.563, 0.146, 0.176) | (0.498, 0.001, 0.142)→(0.575, 0.146, 0.153) | 0.215→0.054 | 1.00 / 27.667 | 0.117 | 0.227 |
| fine_placement | approach | 1.00 / step_budget | (0.563, 0.146, 0.176)→(0.586, 0.185, 0.199) | (0.575, 0.146, 0.153)→(0.592, 0.185, 0.170) | 0.054→0.019 | 1.00 / 25.000 | 0.098 | 0.433 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.154
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.609
- phase_breakdown.lift_score: 0.199
- phase_breakdown.place_score: 0.427
- phase_breakdown.pre_grasp_score: 0.531
- phase_breakdown.place_fine_score: 0.907
- phase_breakdown.grasp_score: 0.769
- grasp_place_fitness: 0.968

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.003
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55263,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12443,"approach_object.approach_speed":0.10062,"approach_object.approach_tolerance":0.05672,"descend_to_grasp.descend_speed":0.15725,"descend_to_grasp.descend_tolerance":0.01482,"descend_to_grasp.grasp_offset_z":0.01149,"fine_placement.place_offset_x":0.00511,"fine_placement.place_offset_y":-0.00053,"fine_placement.place_offset_z":0.02224,"fine_placement.place_speed":0.07322,"fine_placement.place_tolerance":0.01384,"grasp_action.grasp_max_width":0.04993,"lift_object.lift_height":0.17567,"lift_object.lift_speed":0.08386,"lift_object.lift_tolerance":0.04038,"transport_to_goal.transport_speed":0.05265,"transport_to_goal.transport_tolerance":0.03792},"optimized_scores":{"best_composite_score":-0.0027,"best_fitness_score":0.9673,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.51135,-0.02179,-0.00161],"force_p95":0.43499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44779,"mean_force":0.17744,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49924,-0.02164,0.04312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3056.0,"contact_point_centroid":[0.55375,0.15368,0.2221],"force_p95":0.11359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41882,"mean_force":0.08534,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54787,0.13502,0.22034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3137.0,"contact_point_centroid":[0.49946,-0.00251,0.10175],"force_p95":0.12168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3113,"mean_force":0.07414,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49762,-0.02158,0.09905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3477.0,"contact_point_centroid":[0.49952,-0.04055,0.10008],"force_p95":0.1175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28914,"mean_force":0.06949,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49762,-0.02158,0.09819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3289.0,"contact_point_centroid":[0.55331,0.11556,0.22082],"force_p95":0.10655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2752,"mean_force":0.07892,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.54736,0.13401,0.2193]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02284,-0.00212],"force_p95":0.15557,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21639,"mean_force":0.13139,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.5017,-0.0217,0.04332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.52421,0.02869,0.19287],"force_p95":0.11003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15749,"mean_force":0.08238,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51887,0.04716,0.19145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.50107,-0.00246,0.04483],"force_p95":0.08017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14612,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50055,-0.02167,0.04206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2395.0,"contact_point_centroid":[0.52315,0.06287,0.19295],"force_p95":0.1151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13884,"mean_force":0.09033,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51794,0.04419,0.19082]},{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.5137,-0.02302,-0.00161],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1243,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50457,-0.00585,0.26029]},{"body_a":"world","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5076,-0.01771,0.12723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4981.0,"contact_point_centroid":[0.50112,-0.0408,0.04389],"force_p95":0.07253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07559,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50055,-0.02167,0.04206]}],"total_contact_groups":12},"final_pose_error":0.01375,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56372,0.14613,0.20648],"final_tcp_position":[0.5539,0.14631,0.2325],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.44779,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02597],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26565,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":324.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50882,-0.01347,0.20933],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18367,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02597],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26565,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp","tcp_end":[0.50884,-0.02183,0.05137],"tcp_start":[0.50882,-0.01347,0.20933],"tcp_to_object_dist_end":0.02584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.0219,0.0256],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26519,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14974,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.21639,"tcp_end":[0.50052,-0.02167,0.04202],"tcp_start":[0.50884,-0.02183,0.05137],"tcp_to_object_dist_end":0.02102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.51652,-0.02166,0.15959],"object_pos_start":[0.51364,-0.0219,0.0256],"object_to_goal_dist_end":0.188,"object_to_goal_dist_start":0.26519,"object_z_max":0.15891,"peak_contact_force":0.11456,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6678.0,"raw_peak_contact_force":0.44779,"subtask_id":"lift","tcp_end":[0.49799,-0.02157,0.17803],"tcp_start":[0.50052,-0.02167,0.04202],"tcp_to_object_dist_end":0.02615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.55548,0.11897,0.18446],"object_pos_start":[0.51652,-0.02166,0.15959],"object_to_goal_dist_end":0.04979,"object_to_goal_dist_start":0.188,"object_z_max":0.18432,"peak_contact_force":0.11507,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5187.0,"raw_peak_contact_force":0.15749,"subtask_id":"place","tcp_end":[0.54171,0.11913,0.20748],"tcp_start":[0.49799,-0.02157,0.17803],"tcp_to_object_dist_end":0.02682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.56372,0.14613,0.20648],"object_pos_start":[0.55548,0.11897,0.18446],"object_to_goal_dist_end":0.01907,"object_to_goal_dist_start":0.04979,"object_z_max":0.2064,"peak_contact_force":0.08486,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6345.0,"raw_peak_contact_force":0.41882,"subtask_id":"place_fine","tcp_end":[0.5539,0.14631,0.2325],"tcp_start":[0.54171,0.11913,0.20748],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11656,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14037,"approach_object.approach_speed":0.16406,"approach_object.approach_tolerance":0.06162,"descend_to_grasp.descend_speed":0.07076,"descend_to_grasp.descend_tolerance":0.01012,"descend_to_grasp.grasp_offset_z":0.01835,"fine_placement.place_offset_x":0.00622,"fine_placement.place_offset_y":0.00858,"fine_placement.place_offset_z":0.0181,"fine_placement.place_speed":0.08206,"fine_placement.place_tolerance":0.01008,"grasp_action.grasp_max_width":0.04416,"lift_object.lift_height":0.17566,"lift_object.lift_speed":0.08878,"lift_object.lift_tolerance":0.06635,"transport_to_goal.transport_speed":0.15503,"transport_to_goal.transport_tolerance":0.05917},"optimized_scores":{"best_composite_score":-0.07476,"best_fitness_score":0.89524,"best_task_score":0.86091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":12163.0,"contact_point_centroid":[0.56059,0.24225,0.14923],"force_p95":0.09912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48266,"mean_force":0.0731,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.55515,0.22354,0.14813]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.49901,0.043,-0.00172],"force_p95":0.42885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44774,"mean_force":0.2057,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48742,0.0422,0.04561]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11523.0,"contact_point_centroid":[0.56076,0.20468,0.14933],"force_p95":0.09877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38284,"mean_force":0.07499,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.55509,0.2234,0.14808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2347.0,"contact_point_centroid":[0.48635,0.06119,0.09333],"force_p95":0.13471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31415,"mean_force":0.06536,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48627,0.04197,0.09072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1949.0,"contact_point_centroid":[0.48656,0.02275,0.09376],"force_p95":0.13582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27343,"mean_force":0.0719,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4863,0.04198,0.09111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1767.0,"contact_point_centroid":[0.51773,0.08558,0.15542],"force_p95":0.14618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25764,"mean_force":0.0906,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51363,0.10448,0.15276]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.04484,-0.00222],"force_p95":0.1814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24301,"mean_force":0.13834,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49002,0.04244,0.04562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1810.0,"contact_point_centroid":[0.51885,0.12568,0.15429],"force_p95":0.1312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20832,"mean_force":0.08435,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51449,0.10699,0.15238]},{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.50118,0.04505,-0.00148],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1248,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50176,0.01034,0.26811]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4791.0,"contact_point_centroid":[0.48812,0.0231,0.04747],"force_p95":0.07351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.128,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48888,0.04234,0.04439]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12371,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4981,0.03363,0.13541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5372.0,"contact_point_centroid":[0.48878,0.0617,0.0466],"force_p95":0.07548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0789,"mean_force":0.04237,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48889,0.04234,0.0444]}],"total_contact_groups":12},"final_pose_error":0.01058,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57229,0.25005,0.12638],"final_tcp_position":[0.56598,0.24983,0.15609],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":76.72612,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02587],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24196,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.1239,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":248.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50236,0.02384,0.22678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20202,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02587],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24196,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.12371,"subtask_id":"grasp","tcp_end":[0.49683,0.043,0.05307],"tcp_start":[0.50236,0.02384,0.22678],"tcp_to_object_dist_end":0.02747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04319,0.02523],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24381,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17449,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11963.0,"raw_peak_contact_force":0.24301,"tcp_end":[0.48886,0.04233,0.04436],"tcp_start":[0.49683,0.043,0.05307],"tcp_to_object_dist_end":0.02278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.50409,0.04266,0.13506],"object_pos_start":[0.50118,0.04319,0.02523],"object_to_goal_dist_end":0.21133,"object_to_goal_dist_start":0.24381,"object_z_max":0.13385,"peak_contact_force":76.72612,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4362.0,"raw_peak_contact_force":0.44774,"subtask_id":"lift","tcp_end":[0.48819,0.04201,0.15489],"tcp_start":[0.48886,0.04233,0.04436],"tcp_to_object_dist_end":0.02543,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.56125,0.18968,0.12263],"object_pos_start":[0.50409,0.04266,0.13506],"object_to_goal_dist_end":0.06031,"object_to_goal_dist_start":0.21133,"object_z_max":0.14283,"peak_contact_force":0.15168,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3577.0,"raw_peak_contact_force":0.25764,"subtask_id":"place","tcp_end":[0.54446,0.1894,0.14382],"tcp_start":[0.48819,0.04201,0.15489],"tcp_to_object_dist_end":0.02703,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.57229,0.25005,0.12638],"object_pos_start":[0.56125,0.18968,0.12263],"object_to_goal_dist_end":0.02247,"object_to_goal_dist_start":0.06031,"object_z_max":0.12638,"peak_contact_force":0.10023,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23686.0,"raw_peak_contact_force":0.48266,"subtask_id":"place_fine","tcp_end":[0.56598,0.24983,0.15609],"tcp_start":[0.54446,0.1894,0.14382],"tcp_to_object_dist_end":0.03037,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77711,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.0911,"approach_object.approach_speed":0.11292,"approach_object.approach_tolerance":0.04086,"descend_to_grasp.descend_speed":0.16427,"descend_to_grasp.descend_tolerance":0.01241,"descend_to_grasp.grasp_offset_z":0.01349,"fine_placement.place_offset_x":0.01587,"fine_placement.place_offset_y":0.00676,"fine_placement.place_offset_z":0.03413,"fine_placement.place_speed":0.06435,"fine_placement.place_tolerance":0.0106,"grasp_action.grasp_max_width":0.02605,"lift_object.lift_height":0.17036,"lift_object.lift_speed":0.06356,"lift_object.lift_tolerance":0.06391,"transport_to_goal.transport_speed":0.14787,"transport_to_goal.transport_tolerance":0.043},"optimized_scores":{"best_composite_score":-0.00249,"best_fitness_score":0.96751,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.47371,-0.01925,-0.0016],"force_p95":0.42074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47066,"mean_force":0.21269,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46392,-0.01916,0.04435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18040.0,"contact_point_centroid":[0.61985,0.16421,0.19027],"force_p95":0.08879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39855,"mean_force":0.05398,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.62023,0.14548,0.19048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.46378,-0.03833,0.09043],"force_p95":0.12806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2687,"mean_force":0.06423,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46361,-0.01913,0.0886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4461.0,"contact_point_centroid":[0.53471,0.03566,0.1663],"force_p95":0.10342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26672,"mean_force":0.0643,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53445,0.05488,0.16403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2077.0,"contact_point_centroid":[0.46372,7e-05,0.09001],"force_p95":0.126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25759,"mean_force":0.06422,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4636,-0.01913,0.08801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14392.0,"contact_point_centroid":[0.6187,0.12568,0.18899],"force_p95":0.1077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23723,"mean_force":0.06745,"phase_index":5.0,"phase_name":"fine_placement","phase_type":"approach","tcp_position_centroid":[0.61928,0.14468,0.18954]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02007,-0.00208],"force_p95":0.14628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20128,"mean_force":0.12908,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46602,-0.01921,0.04445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4923.0,"contact_point_centroid":[0.5312,0.06999,0.16513],"force_p95":0.09564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17362,"mean_force":0.05736,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53088,0.05101,0.16336]},{"body_a":"world","body_b":"grasp_target","contact_count":608.0,"contact_point_centroid":[0.47616,-0.02015,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12343,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4914,-0.00703,0.23406]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47566,-0.01716,0.1046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5305.0,"contact_point_centroid":[0.46431,7e-05,0.04482],"force_p95":0.06614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11167,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46493,-0.01918,0.04335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5427.0,"contact_point_centroid":[0.46432,-0.03847,0.04469],"force_p95":0.06611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06808,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46493,-0.01918,0.04335]}],"total_contact_groups":12},"final_pose_error":0.02037,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.64107,0.1602,0.17614],"final_tcp_position":[0.63712,0.1594,0.20776],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.47066,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.48122,-0.01501,0.16085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp","tcp_end":[0.47267,-0.01934,0.05128],"tcp_start":[0.48122,-0.01501,0.16085],"tcp_to_object_dist_end":0.02551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01948,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28819,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14366,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12532.0,"raw_peak_contact_force":0.20128,"tcp_end":[0.4649,-0.01918,0.04332],"tcp_start":[0.47267,-0.01934,0.05128],"tcp_to_object_dist_end":0.02088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.47422,-0.01928,0.13152],"object_pos_start":[0.47609,-0.01948,0.02569],"object_to_goal_dist_end":0.24492,"object_to_goal_dist_start":0.28819,"object_z_max":0.13035,"peak_contact_force":0.08423,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4233.0,"raw_peak_contact_force":0.47066,"subtask_id":"lift","tcp_end":[0.46509,-0.01911,0.15004],"tcp_start":[0.4649,-0.01918,0.04332],"tcp_to_object_dist_end":0.02065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.60922,0.12943,0.15313],"object_pos_start":[0.47422,-0.01928,0.13152],"object_to_goal_dist_end":0.05234,"object_to_goal_dist_start":0.24492,"object_z_max":0.15307,"peak_contact_force":0.08462,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9384.0,"raw_peak_contact_force":0.26672,"subtask_id":"place","tcp_end":[0.60374,0.12958,0.17721],"tcp_start":[0.46509,-0.01911,0.15004],"tcp_to_object_dist_end":0.02469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64107,0.1602,0.17614],"object_pos_start":[0.60922,0.12943,0.15313],"object_to_goal_dist_end":0.01693,"object_to_goal_dist_start":0.05234,"object_z_max":0.1761,"peak_contact_force":0.10985,"phase_name":"fine_placement","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32432.0,"raw_peak_contact_force":0.39855,"subtask_id":"place_fine","tcp_end":[0.63712,0.1594,0.20776],"tcp_start":[0.60374,0.12958,0.17721],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```