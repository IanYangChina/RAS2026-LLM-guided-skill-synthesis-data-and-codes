## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12  | -0.3721 | 0.31 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17  | -0.0764 | 0.30 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | -0.1713 | 0.18 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | -0.1730 | 0.17 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8  | 0.1723 | 0.78 | ✅ accepted |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.779, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.172) — your mutation base

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
  weight: 0.3
- id: grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
- id: lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place
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
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place

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

## Design Metrics

- **Composite score**: 0.172
- **task_score** (E): 0.779
- **fitness_score**: 0.862  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.67 | 1.00 | 0.0826 |
| descend_to_grasp | 1.00 | 1.00 | 0.1762 |
| grasp_action | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1458 |
| transport_to_goal | 1.00 | 1.00 | 0.1891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.004, 0.222) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 23.683 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.499, 0.004, 0.222)→(0.493, 0.001, 0.046) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.493, 0.001, 0.046)→(0.485, 0.001, 0.038) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.000 | 0.150 | 0.221 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.001, 0.038)→(0.483, 0.001, 0.183) | (0.497, 0.001, 0.026)→(0.498, 0.001, 0.170) | 0.266→0.210 | 1.00 / 29.000 | 0.101 | 0.518 |
| transport_to_goal | approach | 1.00 / step_budget | (0.483, 0.001, 0.183)→(0.570, 0.162, 0.180) | (0.498, 0.001, 0.170)→(0.579, 0.162, 0.159) | 0.210→0.037 | 1.00 / 31.667 | 0.095 | 0.233 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.790
- phase_score: 0.496
- phase_breakdown.lift_score: 0.748
- phase_breakdown.place_score: 0.530
- phase_breakdown.pre_grasp_score: 0.165
- phase_breakdown.grasp_score: 0.690
- grasp_place_fitness: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.868
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.790
- **Median Q (composite search score)**: 0.176
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.393


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60465,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14718,"approach_object.approach_speed":0.07767,"approach_object.approach_tolerance":0.04413,"descend_to_grasp.descend_speed":0.17611,"descend_to_grasp.descend_tolerance":0.01047,"descend_to_grasp.grasp_offset_z":0.01115,"grasp_action.grasp_max_width":0.03453,"lift_object.lift_height":0.23962,"lift_object.lift_speed":0.05057,"lift_object.lift_tolerance":0.0466,"transport_to_goal.transport_speed":0.22993,"transport_to_goal.transport_tolerance":0.03228},"optimized_scores":{"best_composite_score":0.17769,"best_fitness_score":0.86769,"best_task_score":0.79029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.51061,-0.02186,-0.00164],"force_p95":0.49071,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50857,"mean_force":0.302,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49949,-0.022,0.03795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.49853,-0.00279,0.1316],"force_p95":0.08264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30826,"mean_force":0.05552,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49849,-0.02195,0.1297]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5061.0,"contact_point_centroid":[0.49856,-0.04111,0.13125],"force_p95":0.08327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29198,"mean_force":0.05576,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4985,-0.02195,0.12946]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51372,-0.02284,-0.00209],"force_p95":0.1489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21276,"mean_force":0.12966,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50159,-0.02205,0.03839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4061.0,"contact_point_centroid":[0.52014,0.02659,0.22612],"force_p95":0.08758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16805,"mean_force":0.05791,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51953,0.04572,0.22368]},{"body_a":"world","body_b":"grasp_target","contact_count":360.0,"contact_point_centroid":[0.5137,-0.02302,-0.00165],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12408,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50389,-0.0062,0.2642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.50099,-0.00281,0.03988],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13845,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50042,-0.02202,0.03711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4320.0,"contact_point_centroid":[0.52156,0.06975,0.22518],"force_p95":0.07956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12611,"mean_force":0.05287,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.521,0.05072,0.2231]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50702,-0.01819,0.13002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.50104,-0.04113,0.03894],"force_p95":0.07132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07865,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02202,0.03711]}],"total_contact_groups":10},"final_pose_error":0.0317,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55402,0.12221,0.20251],"final_tcp_position":[0.54295,0.1224,0.21703],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.50857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.026],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26563,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12211,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50795,-0.01411,0.21937],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.026],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26563,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp","tcp_end":[0.50863,-0.0222,0.04616],"tcp_start":[0.50795,-0.01411,0.21937],"tcp_to_object_dist_end":0.02078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02209,0.02568],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26526,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14387,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10842.0,"raw_peak_contact_force":0.21276,"tcp_end":[0.5004,-0.02202,0.03708],"tcp_start":[0.50863,-0.0222,0.04616],"tcp_to_object_dist_end":0.01745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.51034,-0.02205,0.21807],"object_pos_start":[0.51361,-0.02209,0.02568],"object_to_goal_dist_end":0.17917,"object_to_goal_dist_start":0.26526,"object_z_max":0.21727,"peak_contact_force":0.07837,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10168.0,"raw_peak_contact_force":0.50857,"subtask_id":"lift","tcp_end":[0.49921,-0.02195,0.23076],"tcp_start":[0.5004,-0.02202,0.03708],"tcp_to_object_dist_end":0.01687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.55402,0.12221,0.20251],"object_pos_start":[0.51034,-0.02205,0.21807],"object_to_goal_dist_end":0.0353,"object_to_goal_dist_start":0.17917,"object_z_max":0.22067,"peak_contact_force":0.08116,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8381.0,"raw_peak_contact_force":0.16805,"subtask_id":"place","tcp_end":[0.54295,0.1224,0.21703],"tcp_start":[0.49921,-0.02195,0.23076],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13223,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.18263,"approach_object.approach_speed":0.18605,"approach_object.approach_tolerance":0.01591,"descend_to_grasp.descend_speed":0.13546,"descend_to_grasp.descend_tolerance":0.01001,"descend_to_grasp.grasp_offset_z":0.01156,"grasp_action.grasp_max_width":0.0275,"lift_object.lift_height":0.17232,"lift_object.lift_speed":0.08604,"lift_object.lift_tolerance":0.04421,"transport_to_goal.transport_speed":0.15299,"transport_to_goal.transport_tolerance":0.03006},"optimized_scores":{"best_composite_score":0.17617,"best_fitness_score":0.86617,"best_task_score":0.78752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.49877,0.04373,-0.00166],"force_p95":0.50385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51928,"mean_force":0.2157,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48715,0.0431,0.03869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3242.0,"contact_point_centroid":[0.48697,0.06202,0.09432],"force_p95":0.11483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31081,"mean_force":0.06488,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48575,0.0429,0.09225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3370.0,"contact_point_centroid":[0.52234,0.10884,0.15571],"force_p95":0.13874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29586,"mean_force":0.09257,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51743,0.12753,0.15366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2966.0,"contact_point_centroid":[0.48696,0.02377,0.09509],"force_p95":0.11563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27553,"mean_force":0.06835,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48576,0.0429,0.0923]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04485,-0.00216],"force_p95":0.16649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23861,"mean_force":0.13448,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48962,0.04334,0.03881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3742.0,"contact_point_centroid":[0.52383,0.14935,0.15435],"force_p95":0.11561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19151,"mean_force":0.08442,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51866,0.13087,0.15318]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.50118,0.04505,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49864,0.017,0.26313]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49612,0.03978,0.13438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48837,0.02398,0.04073],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12034,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48848,0.04323,0.03758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5539.0,"contact_point_centroid":[0.48819,0.06257,0.04014],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07587,"mean_force":0.04088,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04323,0.03759]}],"total_contact_groups":10},"final_pose_error":0.02958,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56432,0.21819,0.12285],"final_tcp_position":[0.55205,0.21834,0.14244],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":26.69861,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":26.69861,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49822,0.0358,0.22473],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp","tcp_end":[0.49646,0.04395,0.04622],"tcp_start":[0.49822,0.0358,0.22473],"tcp_to_object_dist_end":0.02077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04366,0.02544],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24333,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12372.0,"raw_peak_contact_force":0.23861,"tcp_end":[0.48845,0.04323,0.03755],"tcp_start":[0.49646,0.04395,0.04622],"tcp_to_object_dist_end":0.01754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.50433,0.04311,0.15268],"object_pos_start":[0.50113,0.04366,0.02544],"object_to_goal_dist_end":0.21059,"object_to_goal_dist_start":0.24333,"object_z_max":0.15192,"peak_contact_force":0.11457,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6272.0,"raw_peak_contact_force":0.51928,"subtask_id":"lift","tcp_end":[0.48624,0.04289,0.16619],"tcp_start":[0.48845,0.04323,0.03755],"tcp_to_object_dist_end":0.02258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.56432,0.21819,0.12285],"object_pos_start":[0.50433,0.04311,0.15268],"object_to_goal_dist_end":0.03583,"object_to_goal_dist_start":0.21059,"object_z_max":0.15555,"peak_contact_force":0.10944,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7112.0,"raw_peak_contact_force":0.29586,"subtask_id":"place","tcp_end":[0.55205,0.21834,0.14244],"tcp_start":[0.48624,0.04289,0.16619],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67442,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11862,"approach_object.approach_speed":0.05257,"approach_object.approach_tolerance":0.07525,"descend_to_grasp.descend_speed":0.11593,"descend_to_grasp.descend_tolerance":0.01015,"descend_to_grasp.grasp_offset_z":0.01096,"grasp_action.grasp_max_width":0.04231,"lift_object.lift_height":0.14532,"lift_object.lift_speed":0.07343,"lift_object.lift_tolerance":0.03095,"transport_to_goal.transport_speed":0.14375,"transport_to_goal.transport_tolerance":0.02308},"optimized_scores":{"best_composite_score":0.16317,"best_fitness_score":0.85317,"best_task_score":0.75901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.4741,-0.01889,-0.00157],"force_p95":0.47358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5251,"mean_force":0.17031,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46405,-0.01908,0.03941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4324.0,"contact_point_centroid":[0.463,-0.0381,0.09265],"force_p95":0.09837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30829,"mean_force":0.05902,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46213,-0.01901,0.0908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4014.0,"contact_point_centroid":[0.46293,0.00013,0.09255],"force_p95":0.10117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30263,"mean_force":0.06217,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46215,-0.01901,0.0901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6824.0,"contact_point_centroid":[0.54872,0.05158,0.16767],"force_p95":0.12057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23543,"mean_force":0.08228,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54468,0.07037,0.16621]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02004,-0.00209],"force_p95":0.14882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21191,"mean_force":0.1297,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46634,-0.01913,0.03947]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7353.0,"contact_point_centroid":[0.54923,0.08959,0.16718],"force_p95":0.11357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18232,"mean_force":0.07518,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5453,0.07102,0.16631]},{"body_a":"world","body_b":"grasp_target","contact_count":276.0,"contact_point_centroid":[0.47616,-0.02015,-0.00154],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12464,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49658,-0.00356,0.27131]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4813.0,"contact_point_centroid":[0.4654,9e-05,0.04029],"force_p95":0.07094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12435,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46524,-0.0191,0.03837]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12273,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48008,-0.01474,0.128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.46544,-0.03834,0.04025],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07865,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46524,-0.0191,0.03838]}],"total_contact_groups":10},"final_pose_error":0.02301,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61973,0.14531,0.15285],"final_tcp_position":[0.61619,0.14549,0.17955],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":44.22969,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02591],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28845,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":44.22969,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":276.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.49072,-0.00986,0.22152],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19642,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02591],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28845,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.12273,"subtask_id":"grasp","tcp_end":[0.47298,-0.01926,0.0462],"tcp_start":[0.49072,-0.00986,0.22152],"tcp_to_object_dist_end":0.02045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01936,0.02567],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28814,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14557,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11569.0,"raw_peak_contact_force":0.21191,"tcp_end":[0.46521,-0.0191,0.03834],"tcp_start":[0.47298,-0.01926,0.0462],"tcp_to_object_dist_end":0.0167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.47915,-0.01902,0.13928],"object_pos_start":[0.47608,-0.01936,0.02567],"object_to_goal_dist_end":0.23983,"object_to_goal_dist_start":0.28814,"object_z_max":0.13877,"peak_contact_force":0.10875,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8403.0,"raw_peak_contact_force":0.5251,"subtask_id":"lift","tcp_end":[0.46206,-0.01899,0.15335],"tcp_start":[0.46521,-0.0191,0.03834],"tcp_to_object_dist_end":0.02214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.61973,0.14531,0.15285],"object_pos_start":[0.47915,-0.01902,0.13928],"object_to_goal_dist_end":0.04136,"object_to_goal_dist_start":0.23983,"object_z_max":0.15283,"peak_contact_force":0.09529,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14177.0,"raw_peak_contact_force":0.23543,"subtask_id":"place","tcp_end":[0.61619,0.14549,0.17955],"tcp_start":[0.46206,-0.01899,0.15335],"tcp_to_object_dist_end":0.02694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```