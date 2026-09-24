## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1159 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1076 | 0.90 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.0240 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1377 | 0.95 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1146 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.115) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
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
    approach_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    descend_grasp_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    descend_grasp_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    descend_grasp_z:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
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
  guards:
  - id: grasp_guard
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
    - -0.005
- id: lift
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
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
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
    - 0.07
    orientation:
      mode: keep_current
  parameters:
    approach_goal_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_goal_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    approach_goal_z:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.07
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
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
    place_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_grasp_x: status=consumed; consumers=target.offset.x (add)
    - descend_grasp_y: status=consumed; consumers=target.offset.y (add)
    - descend_grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.07]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_x: status=consumed; consumers=target.offset.x (add)
    - approach_goal_y: status=consumed; consumers=target.offset.y (add)
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (add)
    - place_y: status=consumed; consumers=target.offset.y (add)
    - place_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.115
- **task_score** (E): 1.000
- **fitness_score**: 0.985  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1777 |
| descend_to_grasp | 1.00 | 1.00 | 0.1037 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 1.00 | 1.00 | 0.1861 |
| approach_goal | 0.33 | 1.00 | 0.1616 |
| descend_to_place | 1.00 | 1.00 | 0.1011 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.008, 0.127) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.502, -0.008, 0.127)→(0.504, -0.016, 0.024) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.504, -0.016, 0.024)→(0.495, -0.016, 0.015) | (0.493, -0.015, 0.026)→(0.493, -0.016, 0.024) | 0.281→0.282 | 1.00 / 44.667 | 0.235 | 0.388 |
| lift | lift | 1.00 / step_budget | (0.495, -0.016, 0.015)→(0.489, -0.016, 0.201) | (0.493, -0.016, 0.024)→(0.501, -0.016, 0.203) | 0.282→0.241 | 1.00 / 40.333 | 0.077 | 1.112 |
| approach_goal | approach | 0.33 / step_budget | (0.489, -0.016, 0.201)→(0.579, 0.108, 0.225) | (0.501, -0.016, 0.203)→(0.584, 0.108, 0.213) | 0.241→0.101 | 1.00 / 38.667 | 0.083 | 0.112 |
| descend_to_place | descend | 1.00 / step_budget | (0.579, 0.108, 0.225)→(0.633, 0.171, 0.172) | (0.584, 0.108, 0.213)→(0.636, 0.171, 0.156) | 0.101→0.015 | 1.00 / 37.000 | 0.082 | 0.150 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.231
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.576
- phase_breakdown.lift_object_score: 0.535
- phase_breakdown.reach_object_score: 0.125
- phase_breakdown.place_goal_score: 0.781
- grasp_place_fitness: 0.987

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.987
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.117
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0229,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.00075,"approach_goal.approach_goal_y":-0.0321,"approach_goal.approach_goal_z":0.07876,"approach_goal.approach_speed":0.17679,"approach_object.approach_offset_x":0.01676,"approach_object.approach_offset_y":-0.00476,"approach_object.approach_offset_z":0.07526,"descend_to_grasp.descend_grasp_x":0.01141,"descend_to_grasp.descend_grasp_y":-0.0055,"descend_to_grasp.descend_grasp_z":-0.00788,"descend_to_place.place_x":0.00643,"descend_to_place.place_y":0.00758,"descend_to_place.place_z":0.01172,"lift.lift_height":0.16085,"lift.lift_speed":0.14331},"optimized_scores":{"best_composite_score":0.11037,"best_fitness_score":0.98037,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.47332,-0.02518,-0.00162],"force_p95":0.81616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10479,"mean_force":0.14632,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47326,-0.025,0.01452]},{"body_a":"grasp_target","body_b":"hand","contact_count":516.0,"contact_point_centroid":[0.4891,-0.02547,0.10366],"force_p95":0.14399,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40442,"mean_force":0.08267,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47121,-0.02494,0.06489]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4756,-0.02235,-0.00264],"force_p95":0.28388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33882,"mean_force":0.18129,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47614,-0.02508,0.01323]},{"body_a":"grasp_target","body_b":"hand","contact_count":425.0,"contact_point_centroid":[0.49296,-0.01177,0.05283],"force_p95":0.29733,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32639,"mean_force":0.16509,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47581,-0.02506,0.0129]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14454.0,"contact_point_centroid":[0.47155,-0.00583,0.0904],"force_p95":0.07304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27646,"mean_force":0.05012,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47133,-0.02494,0.08848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14134.0,"contact_point_centroid":[0.47157,-0.0441,0.08884],"force_p95":0.07239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25924,"mean_force":0.0512,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47132,-0.02494,0.08689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14701.0,"contact_point_centroid":[0.59994,0.0981,0.20581],"force_p95":0.09883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14428,"mean_force":0.06549,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59978,0.11726,0.20565]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49383,-0.01128,0.20689]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48461,-0.02412,0.06457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19942.0,"contact_point_centroid":[0.60055,0.13568,0.20637],"force_p95":0.07554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12049,"mean_force":0.0491,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59953,0.11692,0.20573]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16947.0,"contact_point_centroid":[0.52076,0.00502,0.19897],"force_p95":0.08157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10642,"mean_force":0.05923,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52072,0.02424,0.19704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21160.0,"contact_point_centroid":[0.52169,0.04383,0.19892],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09946,"mean_force":0.04861,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52138,0.02487,0.19742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5384.0,"contact_point_centroid":[0.47516,-0.00497,0.01403],"force_p95":0.07517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09627,"mean_force":0.05002,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47499,-0.02502,0.0121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3989.0,"contact_point_centroid":[0.47515,-0.0441,0.01394],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09554,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47496,-0.02503,0.01206]}],"total_contact_groups":14},"final_pose_error":0.01858,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.6299,0.15412,0.17754],"final_tcp_position":[0.62586,0.15396,0.19565],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.10479,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48951,-0.02298,0.11418],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48294,-0.02531,0.01999],"tcp_start":[0.48951,-0.02298,0.11418],"tcp_to_object_dist_end":0.01044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47543,-0.02511,0.02431],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29284,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.18666,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11598.0,"raw_peak_contact_force":0.33882,"tcp_end":[0.47495,-0.02506,0.01205],"tcp_start":[0.48294,-0.02531,0.01999],"tcp_to_object_dist_end":0.01227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.48633,-0.02511,0.17639],"object_pos_start":[0.47543,-0.02511,0.02431],"object_to_goal_dist_end":0.23496,"object_to_goal_dist_start":0.29284,"object_z_max":0.17623,"peak_contact_force":0.0821,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29280.0,"raw_peak_contact_force":1.10479,"subtask_id":"lift_object","tcp_end":[0.47192,-0.02496,0.17092],"tcp_start":[0.47495,-0.02506,0.01205],"tcp_to_object_dist_end":0.01541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5769,0.06945,0.21316],"object_pos_start":[0.48633,-0.02511,0.17639],"object_to_goal_dist_end":0.10753,"object_to_goal_dist_start":0.23496,"object_z_max":0.21314,"peak_contact_force":0.0945,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38107.0,"raw_peak_contact_force":0.10642,"subtask_id":"place_goal","tcp_end":[0.56858,0.0695,0.22487],"tcp_start":[0.47192,-0.02496,0.17092],"tcp_to_object_dist_end":0.01436,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6299,0.15412,0.17754],"object_pos_start":[0.5769,0.06945,0.21316],"object_to_goal_dist_end":0.01356,"object_to_goal_dist_start":0.10753,"object_z_max":0.21316,"peak_contact_force":0.09891,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34643.0,"raw_peak_contact_force":0.14428,"subtask_id":"place_goal","tcp_end":[0.62586,0.15396,0.19565],"tcp_start":[0.56858,0.0695,0.22487],"tcp_to_object_dist_end":0.01856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.00526,"approach_goal.approach_goal_y":-0.01268,"approach_goal.approach_goal_z":0.07713,"approach_goal.approach_speed":0.18317,"approach_object.approach_offset_x":0.01436,"approach_object.approach_offset_y":0.01203,"approach_object.approach_offset_z":0.10559,"descend_to_grasp.descend_grasp_x":0.01814,"descend_to_grasp.descend_grasp_y":0.01044,"descend_to_grasp.descend_grasp_z":-0.00194,"descend_to_place.place_x":0.02903,"descend_to_place.place_y":0.00835,"descend_to_place.place_z":0.00626,"lift.lift_height":0.21425,"lift.lift_speed":0.14964},"optimized_scores":{"best_composite_score":0.11667,"best_fitness_score":0.98667,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.45548,-0.01361,-0.002],"force_p95":0.58384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.11444,"mean_force":0.11931,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46208,-0.01554,0.02103]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45809,-0.0231,-0.00282],"force_p95":0.35469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46208,"mean_force":0.19966,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46522,-0.0156,0.01863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17462.0,"contact_point_centroid":[0.45783,-0.03457,0.11934],"force_p95":0.08304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42063,"mean_force":0.05089,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45762,-0.01539,0.11743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17458.0,"contact_point_centroid":[0.45781,0.0038,0.11925],"force_p95":0.08283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36411,"mean_force":0.04859,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45762,-0.01539,0.1174]},{"body_a":"grasp_target","body_b":"hand","contact_count":93.0,"contact_point_centroid":[0.47827,-0.03955,0.05576],"force_p95":0.16425,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16655,"mean_force":0.14448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46429,-0.0156,0.01773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3566.0,"contact_point_centroid":[0.46435,0.00371,0.02029],"force_p95":0.10053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14086,"mean_force":0.05328,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01559,0.01752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.60643,0.18266,0.15479],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14007,"mean_force":0.04893,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60617,0.16351,0.15301]},{"body_a":"world","body_b":"grasp_target","contact_count":1848.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48529,-0.00631,0.22291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.60645,0.14438,0.15499],"force_p95":0.07133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13834,"mean_force":0.0487,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60617,0.16351,0.15301]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6048.0,"contact_point_centroid":[0.46436,-0.03733,0.01959],"force_p95":0.10346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12712,"mean_force":0.05029,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.0156,0.0176]},{"body_a":"world","body_b":"grasp_target","contact_count":2832.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47023,-0.01433,0.08118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19825.0,"contact_point_centroid":[0.51526,0.03888,0.20825],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12063,"mean_force":0.04978,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51517,0.05804,0.20632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20244.0,"contact_point_centroid":[0.51426,0.07596,0.20837],"force_p95":0.07336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09927,"mean_force":0.04846,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51415,0.05683,0.20654]}],"total_contact_groups":13},"final_pose_error":0.03471,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63461,0.19342,0.11136],"final_tcp_position":[0.63435,0.1935,0.12798],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.11444,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47172,-0.01296,0.14517],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2832.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47181,-0.01567,0.02505],"tcp_start":[0.47172,-0.01296,0.14517],"tcp_to_object_dist_end":0.01703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45805,-0.01536,0.02311],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29644,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.29352,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11507.0,"raw_peak_contact_force":0.46208,"tcp_end":[0.46407,-0.01557,0.01751],"tcp_start":[0.47181,-0.01567,0.02505],"tcp_to_object_dist_end":0.00822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.46629,-0.01535,0.22166],"object_pos_start":[0.45805,-0.01536,0.02311],"object_to_goal_dist_end":0.29731,"object_to_goal_dist_start":0.29644,"object_z_max":0.22148,"peak_contact_force":0.07404,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35110.0,"raw_peak_contact_force":1.11444,"subtask_id":"lift_object","tcp_end":[0.45528,-0.01529,0.22305],"tcp_start":[0.46407,-0.01557,0.01751],"tcp_to_object_dist_end":0.01109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5694,0.12103,0.18223],"object_pos_start":[0.46629,-0.01535,0.22166],"object_to_goal_dist_end":0.12621,"object_to_goal_dist_start":0.29731,"object_z_max":0.22178,"peak_contact_force":0.07403,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40069.0,"raw_peak_contact_force":0.12063,"subtask_id":"place_goal","tcp_end":[0.56889,0.12106,0.1952],"tcp_start":[0.45528,-0.01529,0.22305],"tcp_to_object_dist_end":0.01299,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63461,0.19342,0.11136],"object_pos_start":[0.5694,0.12103,0.18223],"object_to_goal_dist_end":0.01571,"object_to_goal_dist_start":0.12621,"object_z_max":0.18223,"peak_contact_force":0.07001,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.14007,"subtask_id":"place_goal","tcp_end":[0.63435,0.1935,0.12798],"tcp_start":[0.56889,0.12106,0.1952],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02273,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.03938,"approach_goal.approach_goal_y":-0.00921,"approach_goal.approach_goal_z":0.07772,"approach_goal.approach_speed":0.23125,"approach_object.approach_offset_x":0.00899,"approach_object.approach_offset_y":0.0127,"approach_object.approach_offset_z":0.08486,"descend_to_grasp.descend_grasp_x":0.01942,"descend_to_grasp.descend_grasp_y":-0.00995,"descend_to_grasp.descend_grasp_z":-0.00532,"descend_to_place.place_x":-0.00196,"descend_to_place.place_y":0.01108,"descend_to_place.place_z":0.00596,"lift.lift_height":0.20121,"lift.lift_speed":0.13387},"optimized_scores":{"best_composite_score":0.11676,"best_fitness_score":0.98676,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":223.0,"contact_point_centroid":[0.541,-0.00771,-0.00182],"force_p95":0.7735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.11721,"mean_force":0.14707,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54498,-0.00621,0.01915]},{"body_a":"grasp_target","body_b":"hand","contact_count":274.0,"contact_point_centroid":[0.55968,0.01204,0.07701],"force_p95":0.07437,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43595,"mean_force":0.03303,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54265,-0.00626,0.03914]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54409,-0.00147,-0.00255],"force_p95":0.28523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36237,"mean_force":0.17835,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54863,-0.00616,0.01815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18640.0,"contact_point_centroid":[0.5418,0.01277,0.11142],"force_p95":0.07623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34023,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54159,-0.00637,0.10951]},{"body_a":"grasp_target","body_b":"hand","contact_count":336.0,"contact_point_centroid":[0.56389,0.01268,0.05499],"force_p95":0.28026,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29969,"mean_force":0.09094,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54747,-0.00615,0.01679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18640.0,"contact_point_centroid":[0.54183,-0.02553,0.11137],"force_p95":0.07563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28906,"mean_force":0.04899,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54159,-0.00637,0.10951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5996.0,"contact_point_centroid":[0.61881,0.13133,0.22164],"force_p95":0.0812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16438,"mean_force":0.05564,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61901,0.15055,0.22008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7216.0,"contact_point_centroid":[0.61823,0.16884,0.22267],"force_p95":0.06999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14905,"mean_force":0.04753,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61808,0.14983,0.22144]},{"body_a":"world","body_b":"grasp_target","contact_count":2440.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52158,0.00632,0.20943]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54947,0.00253,0.06775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3874.0,"contact_point_centroid":[0.54751,-0.02526,0.01858],"force_p95":0.08495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11361,"mean_force":0.04602,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54731,-0.00615,0.01659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5648.0,"contact_point_centroid":[0.54754,0.01455,0.0186],"force_p95":0.08627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11309,"mean_force":0.05009,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54736,-0.00615,0.01666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17220.0,"contact_point_centroid":[0.5694,0.04626,0.23304],"force_p95":0.08102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10825,"mean_force":0.05745,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56923,0.06546,0.2307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20997.0,"contact_point_centroid":[0.57055,0.08687,0.23318],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10513,"mean_force":0.04851,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57026,0.06788,0.23153]}],"total_contact_groups":14},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64233,0.16475,0.17831],"final_tcp_position":[0.63746,0.16468,0.19366],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.11721,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2440.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.54561,0.01276,0.121],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55607,-0.00612,0.02698],"tcp_start":[0.54561,0.01276,0.121],"tcp_to_object_dist_end":0.01385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54404,-0.00653,0.02406],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25638,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.22373,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11658.0,"raw_peak_contact_force":0.36237,"tcp_end":[0.54729,-0.00619,0.01658],"tcp_start":[0.55607,-0.00612,0.02698],"tcp_to_object_dist_end":0.00816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.55175,-0.00653,0.21167],"object_pos_start":[0.54404,-0.00653,0.02406],"object_to_goal_dist_end":0.19161,"object_to_goal_dist_start":0.25638,"object_z_max":0.21151,"peak_contact_force":0.07483,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37777.0,"raw_peak_contact_force":1.11721,"subtask_id":"lift_object","tcp_end":[0.54079,-0.00653,0.21008],"tcp_start":[0.54729,-0.00619,0.01658],"tcp_to_object_dist_end":0.01107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60609,0.13466,0.24221],"object_pos_start":[0.55175,-0.00653,0.21167],"object_to_goal_dist_end":0.06989,"object_to_goal_dist_start":0.19161,"object_z_max":0.24218,"peak_contact_force":0.08049,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38217.0,"raw_peak_contact_force":0.10825,"subtask_id":"place_goal","tcp_end":[0.59953,0.1347,0.25567],"tcp_start":[0.54079,-0.00653,0.21008],"tcp_to_object_dist_end":0.01497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.64233,0.16475,0.17831],"object_pos_start":[0.60609,0.13466,0.24221],"object_to_goal_dist_end":0.01537,"object_to_goal_dist_start":0.06989,"object_z_max":0.24221,"peak_contact_force":0.07835,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13212.0,"raw_peak_contact_force":0.16438,"subtask_id":"place_goal","tcp_end":[0.63746,0.16468,0.19366],"tcp_start":[0.59953,0.1347,0.25567],"tcp_to_object_dist_end":0.01611,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```