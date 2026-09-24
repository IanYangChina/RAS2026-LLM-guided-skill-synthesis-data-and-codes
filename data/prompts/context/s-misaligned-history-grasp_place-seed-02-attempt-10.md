## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.0240 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1377 | 0.95 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2318 | 0.57 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | time_limit | time_limit | time_limit | 20  | 0.1407 | 0.96 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1076 | 0.90 | ❌ rejected |

**Proposal policy**: task_score is 0.90 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.108) — your mutation base

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

- **Composite score**: 0.108
- **task_score** (E): 0.896
- **fitness_score**: 0.928  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1610 |
| descend_to_grasp | 1.00 | 1.00 | 0.1242 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 0.00 | 1.00 | 0.1623 |
| approach_goal | 0.33 | 1.00 | 0.1433 |
| descend_to_place | 1.00 | 1.00 | 0.0938 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.000, 0.145) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.000, 0.145)→(0.506, -0.011, 0.022) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, -0.011, 0.022)→(0.498, -0.011, 0.013) | (0.493, -0.015, 0.026)→(0.492, -0.011, 0.025) | 0.281→0.279 | 1.00 / 45.000 | 0.175 | 0.295 |
| lift | lift | 0.00 / step_budget | (0.498, -0.011, 0.013)→(0.490, -0.011, 0.175) | (0.492, -0.011, 0.025)→(0.497, -0.011, 0.182) | 0.279→0.235 | 1.00 / 40.333 | 0.072 | 1.112 |
| approach_goal | approach | 0.33 / step_budget | (0.490, -0.011, 0.175)→(0.581, 0.093, 0.208) | (0.497, -0.011, 0.182)→(0.586, 0.093, 0.205) | 0.235→0.111 | 1.00 / 40.000 | 0.074 | 0.097 |
| descend_to_place | descend | 1.00 / step_budget | (0.581, 0.093, 0.208)→(0.621, 0.158, 0.166) | (0.586, 0.093, 0.205)→(0.626, 0.158, 0.159) | 0.111→0.023 | 1.00 / 41.333 | 0.075 | 0.105 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.108
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.600
- phase_breakdown.lift_object_score: 0.823
- phase_breakdown.reach_object_score: 0.114
- phase_breakdown.place_goal_score: 0.661
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.091
- **K-run variance**: 0.0013
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90132,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.00203,"approach_goal.approach_goal_y":-0.01315,"approach_goal.approach_goal_z":0.06651,"approach_goal.approach_speed":0.08819,"approach_object.approach_offset_x":0.03507,"approach_object.approach_offset_y":0.0239,"approach_object.approach_offset_z":0.09911,"descend_to_grasp.descend_grasp_x":0.01705,"descend_to_grasp.descend_grasp_y":0.00344,"descend_to_grasp.descend_grasp_z":-0.00597,"descend_to_place.place_x":0.01452,"descend_to_place.place_y":0.01584,"descend_to_place.place_z":-0.00805,"lift.lift_height":0.22699},"optimized_scores":{"best_composite_score":0.07453,"best_fitness_score":0.89453,"best_task_score":0.82598},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.47278,-0.01448,-0.00151],"force_p95":0.80997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08159,"mean_force":0.12852,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47942,-0.01522,0.01715]},{"body_a":"grasp_target","body_b":"hand","contact_count":598.0,"contact_point_centroid":[0.49242,-0.03463,0.10031],"force_p95":0.08617,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42783,"mean_force":0.04025,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47586,-0.01513,0.06207]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47577,-0.01817,-0.00245],"force_p95":0.26092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30844,"mean_force":0.16667,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48245,-0.01528,0.0159]},{"body_a":"grasp_target","body_b":"hand","contact_count":377.0,"contact_point_centroid":[0.49515,-0.03138,0.05429],"force_p95":0.27949,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30484,"mean_force":0.11069,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48162,-0.01527,0.01507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47535,-0.03424,0.09688],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29566,"mean_force":0.0493,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47512,-0.0151,0.095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47533,0.00404,0.09689],"force_p95":0.07105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27615,"mean_force":0.04877,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47512,-0.0151,0.095]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.1329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50218,0.00164,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":2240.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49633,-0.00596,0.07823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21402.0,"contact_point_centroid":[0.582,0.12614,0.19238],"force_p95":0.06786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09723,"mean_force":0.04618,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58215,0.10697,0.19008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20894.0,"contact_point_centroid":[0.58151,0.08734,0.19258],"force_p95":0.07006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09669,"mean_force":0.04717,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58176,0.10653,0.1902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5384.0,"contact_point_centroid":[0.4815,-0.03529,0.01665],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09421,"mean_force":0.04903,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48129,-0.01527,0.01474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.51034,0.00704,0.19376],"force_p95":0.07086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09349,"mean_force":0.04905,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51008,0.02618,0.19188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4063.0,"contact_point_centroid":[0.48144,0.00382,0.01665],"force_p95":0.07436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09295,"mean_force":0.04511,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48126,-0.01527,0.01471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.51032,0.04531,0.19376],"force_p95":0.07166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08366,"mean_force":0.04892,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51008,0.02618,0.19188]}],"total_contact_groups":14},"final_pose_error":0.04891,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61778,0.14009,0.17354],"final_tcp_position":[0.6117,0.14011,0.18126],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.08159,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50649,0.00337,0.13782],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2240.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48932,-0.01531,0.02286],"tcp_start":[0.50649,0.00337,0.13782],"tcp_to_object_dist_end":0.01438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47543,-0.01505,0.02463],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28644,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.18464,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11624.0,"raw_peak_contact_force":0.30844,"tcp_end":[0.48124,-0.01524,0.01469],"tcp_start":[0.48932,-0.01531,0.02286],"tcp_to_object_dist_end":0.01151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48114,-0.01503,0.18177],"object_pos_start":[0.47543,-0.01505,0.02463],"object_to_goal_dist_end":0.23023,"object_to_goal_dist_start":0.28644,"object_z_max":0.18158,"peak_contact_force":0.07251,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40765.0,"raw_peak_contact_force":1.08159,"subtask_id":"lift_object","tcp_end":[0.4734,-0.01503,0.177],"tcp_start":[0.48124,-0.01524,0.01469],"tcp_to_object_dist_end":0.00909,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55204,0.06087,0.20629],"object_pos_start":[0.48114,-0.01503,0.18177],"object_to_goal_dist_end":0.12741,"object_to_goal_dist_start":0.23023,"object_z_max":0.20626,"peak_contact_force":0.07211,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.09349,"subtask_id":"place_goal","tcp_end":[0.54381,0.06086,0.20807],"tcp_start":[0.4734,-0.01503,0.177],"tcp_to_object_dist_end":0.00842,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61778,0.14009,0.17354],"object_pos_start":[0.55204,0.06087,0.20629],"object_to_goal_dist_end":0.02868,"object_to_goal_dist_start":0.12741,"object_z_max":0.20629,"peak_contact_force":0.07898,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":42296.0,"raw_peak_contact_force":0.09723,"subtask_id":"place_goal","tcp_end":[0.6117,0.14011,0.18126],"tcp_start":[0.54381,0.06086,0.20807],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04027,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.00591,"approach_goal.approach_goal_y":-0.00047,"approach_goal.approach_goal_z":0.09631,"approach_goal.approach_speed":0.16227,"approach_object.approach_offset_x":0.00603,"approach_object.approach_offset_y":0.01688,"approach_object.approach_offset_z":0.12085,"descend_to_grasp.descend_grasp_x":0.01874,"descend_to_grasp.descend_grasp_y":-0.00185,"descend_to_grasp.descend_grasp_z":-0.01866,"descend_to_place.place_x":0.00211,"descend_to_place.place_y":0.006,"descend_to_place.place_z":-0.00279,"lift.lift_height":0.20461},"optimized_scores":{"best_composite_score":0.09056,"best_fitness_score":0.91056,"best_task_score":0.86247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.45539,-0.02536,-0.00134],"force_p95":0.86427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07102,"mean_force":0.12422,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46169,-0.02536,0.01574]},{"body_a":"grasp_target","body_b":"hand","contact_count":773.0,"contact_point_centroid":[0.47452,-0.02894,0.11376],"force_p95":0.11773,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41208,"mean_force":0.0591,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45763,-0.02526,0.0752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45741,-0.04441,0.09557],"force_p95":0.06996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27082,"mean_force":0.0493,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45719,-0.02526,0.09372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.4574,-0.00613,0.09564],"force_p95":0.06952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27077,"mean_force":0.04906,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45719,-0.02526,0.09372]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4581,-0.02585,-0.00237],"force_p95":0.16893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2147,"mean_force":0.14908,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46454,-0.02545,0.01459]},{"body_a":"grasp_target","body_b":"hand","contact_count":395.0,"contact_point_centroid":[0.47711,-0.03092,0.05373],"force_p95":0.13119,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20654,"mean_force":0.11446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46388,-0.02543,0.01396]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48193,-0.00411,0.23073]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46684,-0.0181,0.08043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.58278,0.13546,0.14625],"force_p95":0.07023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10845,"mean_force":0.04856,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5825,0.15459,0.14429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.58277,0.17374,0.1461],"force_p95":0.07217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10502,"mean_force":0.04879,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5825,0.15459,0.14429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.50196,0.02404,0.18222],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09909,"mean_force":0.04926,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5017,0.04319,0.18036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.4636,-0.04469,0.01536],"force_p95":0.06824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09354,"mean_force":0.0457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4634,-0.02542,0.01349]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.50192,0.06232,0.18226],"force_p95":0.07455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08498,"mean_force":0.04911,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5017,0.04319,0.18036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4730.0,"contact_point_centroid":[0.46357,-0.00626,0.01541],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07085,"mean_force":0.04437,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46339,-0.02542,0.01349]}],"total_contact_groups":14},"final_pose_error":0.0303,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.6156,0.19241,0.10847],"final_tcp_position":[0.61187,0.19242,0.11661],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.07102,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4646,-0.00848,0.16053],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47108,-0.02567,0.02094],"tcp_start":[0.4646,-0.00848,0.16053],"tcp_to_object_dist_end":0.01352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45765,-0.02542,0.02508],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30374,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1549,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11885.0,"raw_peak_contact_force":0.2147,"tcp_end":[0.46336,-0.02541,0.01346],"tcp_start":[0.47108,-0.02567,0.02094],"tcp_to_object_dist_end":0.01295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46361,-0.02528,0.18147],"object_pos_start":[0.45765,-0.02542,0.02508],"object_to_goal_dist_end":0.29459,"object_to_goal_dist_start":0.30374,"object_z_max":0.18128,"peak_contact_force":0.07189,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40927.0,"raw_peak_contact_force":1.07102,"subtask_id":"lift_object","tcp_end":[0.45527,-0.02525,0.17536],"tcp_start":[0.46336,-0.02541,0.01346],"tcp_to_object_dist_end":0.01033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55045,0.10289,0.18464],"object_pos_start":[0.46361,-0.02528,0.18147],"object_to_goal_dist_end":0.14972,"object_to_goal_dist_start":0.29459,"object_z_max":0.18463,"peak_contact_force":0.07641,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.09909,"subtask_id":"place_goal","tcp_end":[0.54513,0.10282,0.18822],"tcp_start":[0.45527,-0.02525,0.17536],"tcp_to_object_dist_end":0.00642,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6156,0.19241,0.10847],"object_pos_start":[0.55045,0.10289,0.18464],"object_to_goal_dist_end":0.02219,"object_to_goal_dist_start":0.14972,"object_z_max":0.18464,"peak_contact_force":0.07113,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.10845,"subtask_id":"place_goal","tcp_end":[0.61187,0.19242,0.11661],"tcp_start":[0.54513,0.10282,0.18822],"tcp_to_object_dist_end":0.00895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88406,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.02636,"approach_goal.approach_goal_y":-0.02502,"approach_goal.approach_goal_z":0.05702,"approach_goal.approach_speed":0.19996,"approach_object.approach_offset_x":0.02302,"approach_object.approach_offset_y":0.00592,"approach_object.approach_offset_z":0.10167,"descend_to_grasp.descend_grasp_x":0.01998,"descend_to_grasp.descend_grasp_y":0.00729,"descend_to_grasp.descend_grasp_z":-0.01713,"descend_to_place.place_x":-0.00783,"descend_to_place.place_y":-0.00739,"descend_to_place.place_z":0.01056,"lift.lift_height":0.20097},"optimized_scores":{"best_composite_score":0.1578,"best_fitness_score":0.9778,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.5403,0.00788,-0.00161],"force_p95":0.83028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18301,"mean_force":0.15075,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54695,0.0076,0.0143]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.55954,0.00722,0.13011],"force_p95":0.14642,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41795,"mean_force":0.0853,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54235,0.00756,0.09128]},{"body_a":"grasp_target","body_b":"hand","contact_count":394.0,"contact_point_centroid":[0.56272,-0.00793,0.05278],"force_p95":0.33718,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3605,"mean_force":0.18101,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54977,0.00765,0.01248]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54364,0.00405,-0.0026],"force_p95":0.30504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.338,"mean_force":0.18534,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.55054,0.00768,0.01338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54257,0.0267,0.09314],"force_p95":0.06986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2821,"mean_force":0.0494,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54235,0.00756,0.09128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.5426,-0.01157,0.09319],"force_p95":0.06984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27595,"mean_force":0.04941,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54235,0.00756,0.09128]},{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52817,0.00321,0.21694]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.55677,0.0073,0.06704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2960.0,"contact_point_centroid":[0.64608,0.14641,0.21458],"force_p95":0.0718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10796,"mean_force":0.04838,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64584,0.12726,0.21282]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2960.0,"contact_point_centroid":[0.64617,0.10813,0.21481],"force_p95":0.07118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09875,"mean_force":0.04834,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64584,0.12726,0.21282]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5564.0,"contact_point_centroid":[0.54947,-0.01296,0.0138],"force_p95":0.07689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09791,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54925,0.00762,0.01188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.59661,0.04364,0.20132],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09739,"mean_force":0.04859,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59635,0.06277,0.19938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.59661,0.08191,0.2012],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09733,"mean_force":0.04879,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59635,0.06277,0.19938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3766.0,"contact_point_centroid":[0.5494,0.02666,0.0137],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08829,"mean_force":0.04442,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5492,0.00762,0.01182]},{"body_a":"grasp_target","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.56012,0.00568,0.21155],"force_p95":0.0438,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04611,"mean_force":0.01783,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54181,0.00875,0.17418]}],"total_contact_groups":15},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64365,0.141,0.19439],"final_tcp_position":[0.63964,0.14094,0.19954],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.18301,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.55868,0.00647,0.13643],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55811,0.00796,0.02234],"tcp_start":[0.55868,0.00647,0.13643],"tcp_to_object_dist_end":0.01583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54322,0.00773,0.0244],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24758,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.18415,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11524.0,"raw_peak_contact_force":0.3605,"tcp_end":[0.54919,0.00767,0.0118],"tcp_start":[0.55811,0.00796,0.02234],"tcp_to_object_dist_end":0.01395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54654,0.00762,0.18148],"object_pos_start":[0.54322,0.00773,0.0244],"object_to_goal_dist_end":0.18152,"object_to_goal_dist_start":0.24758,"object_z_max":0.18129,"peak_contact_force":0.07038,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41196.0,"raw_peak_contact_force":1.18301,"subtask_id":"lift_object","tcp_end":[0.54049,0.0076,0.1738],"tcp_start":[0.54919,0.00767,0.0118],"tcp_to_object_dist_end":0.00977,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.65645,0.11539,0.22416],"object_pos_start":[0.54654,0.00762,0.18148],"object_to_goal_dist_end":0.05471,"object_to_goal_dist_start":0.18152,"object_z_max":0.22413,"peak_contact_force":0.07332,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40019.0,"raw_peak_contact_force":0.09739,"subtask_id":"place_goal","tcp_end":[0.65265,0.11529,0.2287],"tcp_start":[0.54049,0.0076,0.1738],"tcp_to_object_dist_end":0.00592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.64365,0.141,0.19439],"object_pos_start":[0.65645,0.11539,0.22416],"object_to_goal_dist_end":0.01785,"object_to_goal_dist_start":0.05471,"object_z_max":0.22416,"peak_contact_force":0.07376,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5920.0,"raw_peak_contact_force":0.10796,"subtask_id":"place_goal","tcp_end":[0.63964,0.14094,0.19954],"tcp_start":[0.65265,0.11529,0.2287],"tcp_to_object_dist_end":0.00653,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```