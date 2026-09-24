## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1076 | 0.90 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.0240 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1377 | 0.95 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2318 | 0.57 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | time_limit | time_limit | time_limit | 20  | 0.1159 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.116) — your mutation base

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

- **Composite score**: 0.116
- **task_score** (E): 1.000
- **fitness_score**: 0.986  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1631 |
| descend_to_grasp | 1.00 | 1.00 | 0.1221 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 0.33 | 1.00 | 0.1628 |
| approach_goal | 0.33 | 1.00 | 0.0918 |
| descend_to_place | 1.00 | 1.00 | 0.0433 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, -0.030, 0.146) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.499, -0.030, 0.146)→(0.503, -0.015, 0.025) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.333 | 0.134 | 0.134 |
| grasp | grasp | 1.00 / step_budget | (0.503, -0.015, 0.025)→(0.495, -0.015, 0.016) | (0.493, -0.015, 0.026)→(0.492, -0.015, 0.022) | 0.281→0.283 | 1.00 / 38.000 | 0.345 | 0.572 |
| lift | lift | 0.33 / step_budget | (0.495, -0.015, 0.016)→(0.489, -0.015, 0.179) | (0.492, -0.015, 0.022)→(0.499, -0.015, 0.179) | 0.283→0.239 | 1.00 / 38.333 | 0.081 | 1.939 |
| approach_goal | approach | 0.33 / step_budget | (0.576, 0.104, 0.207)→(0.629, 0.175, 0.220) | (0.499, -0.015, 0.179)→(0.582, 0.104, 0.195) | 0.239→0.095 | 1.00 / 34.667 | 0.091 | 0.146 |
| descend_to_place | descend | 1.00 / step_budget | (0.629, 0.175, 0.220)→(0.635, 0.175, 0.178) | (0.629, 0.175, 0.199)→(0.633, 0.175, 0.157) | 0.037→0.010 | 1.00 / 29.333 | 0.096 | 0.137 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.351
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.581
- phase_breakdown.lift_object_score: 0.677
- phase_breakdown.reach_object_score: 0.137
- phase_breakdown.place_goal_score: 0.700
- grasp_place_fitness: 0.995

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.995
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.123
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90446,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.0161,"approach_goal.approach_goal_y":0.00243,"approach_goal.approach_goal_z":0.07398,"approach_goal.approach_speed":0.2094,"approach_object.approach_offset_x":0.00478,"approach_object.approach_offset_y":-0.03286,"approach_object.approach_offset_z":0.10386,"descend_to_grasp.descend_grasp_x":0.01785,"descend_to_grasp.descend_grasp_y":-0.00829,"descend_to_grasp.descend_grasp_z":-0.01118,"descend_to_place.place_x":0.00226,"descend_to_place.place_y":0.0014,"descend_to_place.place_z":0.00664,"lift.lift_height":0.22161,"lift.lift_speed":0.08688},"optimized_scores":{"best_composite_score":0.12324,"best_fitness_score":0.99324,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.47267,-0.03298,-0.00224],"force_p95":0.53891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8948,"mean_force":0.12766,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47681,-0.03069,0.02415]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47581,-0.02252,-0.003],"force_p95":0.37695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45342,"mean_force":0.20358,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48036,-0.03084,0.0216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47408,-0.01136,0.0919],"force_p95":0.08321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39805,"mean_force":0.05075,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47387,-0.03054,0.0899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19955.0,"contact_point_centroid":[0.47409,-0.04975,0.09184],"force_p95":0.08291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31649,"mean_force":0.04831,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47387,-0.03054,0.09005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1981.0,"contact_point_centroid":[0.63828,0.17703,0.23232],"force_p95":0.12182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16777,"mean_force":0.0694,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63857,0.15843,0.23337]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1731.0,"contact_point_centroid":[0.63744,0.13935,0.233],"force_p95":0.12648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15739,"mean_force":0.07597,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63866,0.15844,0.23382]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48865,-0.02366,0.22103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3395.0,"contact_point_centroid":[0.47952,-0.05037,0.0244],"force_p95":0.10856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13085,"mean_force":0.06179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47919,-0.03078,0.02042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5514.0,"contact_point_centroid":[0.47946,-0.00929,0.02177],"force_p95":0.11124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12473,"mean_force":0.05263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47925,-0.03078,0.02049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36687.0,"contact_point_centroid":[0.56521,0.05541,0.21122],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12435,"mean_force":0.04948,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56505,0.07456,0.20939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":37497.0,"contact_point_centroid":[0.56675,0.09527,0.21203],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12354,"mean_force":0.04878,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56652,0.07616,0.21021]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48211,-0.03836,0.07472]}],"total_contact_groups":12},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62476,0.15862,0.18019],"final_tcp_position":[0.63364,0.159,0.20631],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.8948,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47881,-0.04842,0.14221],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48703,-0.03115,0.02841],"tcp_start":[0.47881,-0.04842,0.14221],"tcp_to_object_dist_end":0.01565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47563,-0.03058,0.02248],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29724,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.32166,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10709.0,"raw_peak_contact_force":0.45342,"tcp_end":[0.47917,-0.03079,0.0204],"tcp_start":[0.48703,-0.03115,0.02841],"tcp_to_object_dist_end":0.00411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48078,-0.03043,0.16024],"object_pos_start":[0.47563,-0.03058,0.02248],"object_to_goal_dist_end":0.244,"object_to_goal_dist_start":0.29724,"object_z_max":0.16008,"peak_contact_force":0.07712,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40203.0,"raw_peak_contact_force":0.8948,"subtask_id":"lift_object","tcp_end":[0.47296,-0.03047,0.16139],"tcp_start":[0.47917,-0.03079,0.0204],"tcp_to_object_dist_end":0.0079,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1866.0,"n_steps_budget":1000.0,"object_pos_end":[0.58469,0.09184,0.20711],"object_pos_start":[0.48078,-0.03043,0.16024],"object_to_goal_dist_end":0.08374,"object_to_goal_dist_start":0.244,"object_z_max":0.22884,"peak_contact_force":0.08825,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":74184.0,"raw_peak_contact_force":0.12435,"subtask_id":"place_goal","tcp_end":[0.64225,0.15822,0.2531],"tcp_start":[0.58114,0.09165,0.2195],"tcp_to_object_dist_end":0.09917,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.62476,0.15862,0.18019],"object_pos_start":[0.63865,0.1582,0.22885],"object_to_goal_dist_end":0.01189,"object_to_goal_dist_start":0.03951,"object_z_max":0.22885,"peak_contact_force":0.10884,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.16777,"subtask_id":"place_goal","tcp_end":[0.63364,0.159,0.20631],"tcp_start":[0.64225,0.15822,0.2531],"tcp_to_object_dist_end":0.02759,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88554,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.01128,"approach_goal.approach_goal_y":0.00887,"approach_goal.approach_goal_z":0.06226,"approach_goal.approach_speed":0.13344,"approach_object.approach_offset_x":0.02337,"approach_object.approach_offset_y":-0.03176,"approach_object.approach_offset_z":0.1289,"descend_to_grasp.descend_grasp_x":0.0198,"descend_to_grasp.descend_grasp_y":-0.0068,"descend_to_grasp.descend_grasp_z":-0.01334,"descend_to_place.place_x":0.00768,"descend_to_place.place_y":-0.00468,"descend_to_place.place_z":0.00559,"lift.lift_height":0.21682,"lift.lift_speed":0.10923},"optimized_scores":{"best_composite_score":0.09919,"best_fitness_score":0.96919,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":36.0,"contact_point_centroid":[0.4734,-0.0581,-0.0002],"force_p95":4.0119,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.09951,"mean_force":1.43156,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46559,-0.03327,0.00691]},{"body_a":"world","body_b":"right_finger","contact_count":32.0,"contact_point_centroid":[0.47341,-0.00836,-0.00015],"force_p95":3.36962,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.40588,"mean_force":1.32488,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46563,-0.03327,0.00687]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.45606,-0.03166,-0.00164],"force_p95":0.61251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12412,"mean_force":0.21117,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46414,-0.03313,0.00954]},{"body_a":"world","body_b":"left_finger","contact_count":1220.0,"contact_point_centroid":[0.4738,-0.06208,-0.00023],"force_p95":0.35663,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.69054,"mean_force":0.29347,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46598,-0.03332,0.00684]},{"body_a":"grasp_target","body_b":"hand","contact_count":450.0,"contact_point_centroid":[0.47652,-0.02735,0.05027],"force_p95":0.29145,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52265,"mean_force":0.26729,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46705,-0.03336,0.00786]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.47519,-0.03109,0.13474],"force_p95":0.25393,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49405,"mean_force":0.15541,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45862,-0.03179,0.09464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45882,-0.01259,0.09658],"force_p95":0.07114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30275,"mean_force":0.05035,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45862,-0.03179,0.09464]},{"body_a":"world","body_b":"right_finger","contact_count":1157.0,"contact_point_centroid":[0.47375,-0.00476,-0.00017],"force_p95":0.28112,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.29315,"mean_force":0.22696,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46596,-0.03332,0.00682]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45717,-0.02694,-0.00291],"force_p95":0.22604,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24952,"mean_force":0.18976,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46705,-0.03336,0.00786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19356.0,"contact_point_centroid":[0.45865,-0.0509,0.09933],"force_p95":0.07072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16255,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45842,-0.03175,0.0975]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15553,"mean_force":0.12309,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4753,-0.04271,0.0865]},{"body_a":"grasp_target","body_b":"hand","contact_count":199.0,"contact_point_centroid":[0.47827,-0.00826,0.21893],"force_p95":0.06707,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14724,"mean_force":0.03077,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46368,-0.01455,0.18091]},{"body_a":"world","body_b":"grasp_target","contact_count":1768.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48936,-0.02551,0.23334]},{"body_a":"grasp_target","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.47846,-0.04627,0.05521],"force_p95":0.13427,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13567,"mean_force":0.11318,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4738,-0.03386,0.01569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":37740.0,"contact_point_centroid":[0.53361,0.07407,0.1749],"force_p95":0.07292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11688,"mean_force":0.04897,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53335,0.09323,0.17302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":37740.0,"contact_point_centroid":[0.53359,0.11236,0.1749],"force_p95":0.0758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0972,"mean_force":0.04901,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53335,0.09323,0.17302]}],"total_contact_groups":19},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62771,0.20382,0.11149],"final_tcp_position":[0.628,0.20383,0.12102],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":4.09951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1768.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48011,-0.05243,0.1667],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.45848,-0.02625,0.02564],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30375,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15553,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3335.0,"raw_peak_contact_force":0.15553,"subtask_id":"reach_object","tcp_end":[0.4737,-0.03368,0.01431],"tcp_start":[0.48011,-0.05243,0.1667],"tcp_to_object_dist_end":0.02038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45729,-0.02999,0.0242],"object_pos_start":[0.45848,-0.02625,0.02564],"object_to_goal_dist_end":0.30774,"object_to_goal_dist_start":0.30375,"object_z_max":0.02564,"peak_contact_force":0.28368,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8459.0,"raw_peak_contact_force":0.69054,"tcp_end":[0.46588,-0.03329,0.00674],"tcp_start":[0.4737,-0.03368,0.01431],"tcp_to_object_dist_end":0.01973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4632,-0.03057,0.19469],"object_pos_start":[0.45729,-0.02999,0.0242],"object_to_goal_dist_end":0.30228,"object_to_goal_dist_start":0.30774,"object_z_max":0.19455,"peak_contact_force":0.07084,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40609.0,"raw_peak_contact_force":4.09951,"subtask_id":"lift_object","tcp_end":[0.45572,-0.03053,0.18506],"tcp_start":[0.46588,-0.03329,0.00674],"tcp_to_object_dist_end":0.01219,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1887.0,"n_steps_budget":1000.0,"object_pos_end":[0.54543,0.097,0.17663],"object_pos_start":[0.4632,-0.03057,0.19469],"object_to_goal_dist_end":0.15314,"object_to_goal_dist_start":0.30228,"object_z_max":0.19474,"peak_contact_force":0.07429,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":75679.0,"raw_peak_contact_force":0.14724,"subtask_id":"place_goal","tcp_end":[0.61224,0.21173,0.16747],"tcp_start":[0.53616,0.09681,0.17409],"tcp_to_object_dist_end":0.13308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.62771,0.20382,0.11149],"object_pos_start":[0.61118,0.21177,0.15867],"object_to_goal_dist_end":0.00566,"object_to_goal_dist_start":0.04855,"object_z_max":0.15867,"peak_contact_force":0.073,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7000.0,"raw_peak_contact_force":0.09294,"subtask_id":"place_goal","tcp_end":[0.628,0.20383,0.12102],"tcp_start":[0.61224,0.21173,0.16747],"tcp_to_object_dist_end":0.00953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73826,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.0103,"approach_goal.approach_goal_y":-0.00018,"approach_goal.approach_goal_z":0.05726,"approach_goal.approach_speed":0.16309,"approach_object.approach_offset_x":0.00138,"approach_object.approach_offset_y":0.0114,"approach_object.approach_offset_z":0.09212,"descend_to_grasp.descend_grasp_x":0.01496,"descend_to_grasp.descend_grasp_y":0.0196,"descend_to_grasp.descend_grasp_z":-0.01224,"descend_to_place.place_x":0.00374,"descend_to_place.place_y":0.00842,"descend_to_place.place_z":0.01488,"lift.lift_height":0.18479,"lift.lift_speed":0.12413},"optimized_scores":{"best_composite_score":0.1252,"best_fitness_score":0.9952,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":294.0,"contact_point_centroid":[0.54007,0.01707,-0.00299],"force_p95":0.43014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82207,"mean_force":0.16507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53838,0.01784,0.02627]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54421,0.0049,-0.00363],"force_p95":0.49425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57255,"mean_force":0.25343,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54232,0.01809,0.02366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16844.0,"contact_point_centroid":[0.53826,-0.00199,0.10611],"force_p95":0.09388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44388,"mean_force":0.05524,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5378,0.01723,0.10437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16059.0,"contact_point_centroid":[0.53813,0.03659,0.10333],"force_p95":0.09407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34545,"mean_force":0.05362,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53772,0.01725,0.10106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.5407,0.0383,0.02795],"force_p95":0.12952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16643,"mean_force":0.07721,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54103,0.01801,0.02215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":25393.0,"contact_point_centroid":[0.59655,0.08053,0.21671],"force_p95":0.10935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16627,"mean_force":0.07203,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59356,0.09948,0.21584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5656.0,"contact_point_centroid":[0.54164,-0.00659,0.02265],"force_p95":0.12881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.156,"mean_force":0.06241,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54126,0.01803,0.02242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1354.0,"contact_point_centroid":[0.64303,0.13968,0.22289],"force_p95":0.10798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15037,"mean_force":0.07959,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63711,0.15839,0.2228]},{"body_a":"world","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51794,0.00567,0.21359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":30656.0,"contact_point_centroid":[0.59696,0.12008,0.21703],"force_p95":0.09111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13139,"mean_force":0.05667,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59492,0.10147,0.21654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1499.0,"contact_point_centroid":[0.64116,0.17702,0.22237],"force_p95":0.10398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13044,"mean_force":0.0754,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63703,0.15833,0.2231]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54277,0.01527,0.07352]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64798,0.16243,0.17889],"final_tcp_position":[0.64262,0.16211,0.2077],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.82207,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2288.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53838,0.0115,0.12877],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.54966,0.01849,0.03236],"tcp_start":[0.53838,0.0115,0.12877],"tcp_to_object_dist_end":0.01924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54312,0.01678,0.02056],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24489,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.42991,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10108.0,"raw_peak_contact_force":0.57255,"tcp_end":[0.54102,0.01804,0.02213],"tcp_start":[0.54966,0.01849,0.03236],"tcp_to_object_dist_end":0.00291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.55281,0.01658,0.1826],"object_pos_start":[0.54312,0.01678,0.02056],"object_to_goal_dist_end":0.17054,"object_to_goal_dist_start":0.24489,"object_z_max":0.18246,"peak_contact_force":0.0936,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33197.0,"raw_peak_contact_force":0.82207,"subtask_id":"lift_object","tcp_end":[0.53942,0.01668,0.19077],"tcp_start":[0.54102,0.01804,0.02213],"tcp_to_object_dist_end":0.01568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1760.0,"n_steps_budget":1000.0,"object_pos_end":[0.61658,0.12338,0.20261],"object_pos_start":[0.55281,0.01658,0.1826],"object_to_goal_dist_end":0.04796,"object_to_goal_dist_start":0.17054,"object_z_max":0.21002,"peak_contact_force":0.10977,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":56049.0,"raw_peak_contact_force":0.16627,"subtask_id":"place_goal","tcp_end":[0.63298,0.15538,0.23816],"tcp_start":[0.61052,0.12327,0.22623],"tcp_to_object_dist_end":0.05056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.64798,0.16243,0.17889],"object_pos_start":[0.63713,0.15556,0.21003],"object_to_goal_dist_end":0.01297,"object_to_goal_dist_start":0.02179,"object_z_max":0.21003,"peak_contact_force":0.1064,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2853.0,"raw_peak_contact_force":0.15037,"subtask_id":"place_goal","tcp_end":[0.64262,0.16211,0.2077],"tcp_start":[0.63298,0.15538,0.23816],"tcp_to_object_dist_end":0.02931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```