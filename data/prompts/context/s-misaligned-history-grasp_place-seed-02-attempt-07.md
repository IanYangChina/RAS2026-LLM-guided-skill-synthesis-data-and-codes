## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | time_limit | time_limit | time_limit | 20  | 0.1407 | 0.96 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1660 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1129 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2015 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | -0.2318 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.232) — your mutation base

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

- **Composite score**: -0.232
- **task_score** (E): 0.574
- **fitness_score**: 0.768  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1816 |
| descend_to_grasp | 1.00 | 1.00 | 0.1090 |
| grasp | 1.00 | 1.00 | 0.0080 |
| lift | 1.00 | 1.00 | 0.1559 |
| approach_goal | 1.00 | 1.00 | 0.1247 |
| descend_to_place | 1.00 | 1.00 | 0.0817 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.488, -0.018, 0.125) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / time_limit | (0.488, -0.018, 0.125)→(0.503, -0.012, 0.022) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.025) | 0.281→0.281 | 1.00 / 4.333 | 0.187 | 0.206 |
| grasp | grasp | 1.00 / step_budget | (0.502, -0.012, 0.020)→(0.496, -0.012, 0.014) | (0.493, -0.015, 0.025)→(0.493, -0.013, 0.024) | 0.281→0.281 | 1.00 / 39.333 | 0.505 | 0.541 |
| lift | lift | 1.00 / time_limit | (0.496, -0.012, 0.014)→(0.490, -0.013, 0.170) | (0.493, -0.013, 0.024)→(0.499, -0.013, 0.172) | 0.281→0.236 | 1.00 / 39.333 | 0.075 | 1.523 |
| approach_goal | approach | 1.00 / time_limit | (0.490, -0.013, 0.170)→(0.559, 0.087, 0.190) | (0.499, -0.013, 0.172)→(0.567, 0.087, 0.181) | 0.236→0.115 | 1.00 / 35.667 | 0.090 | 0.116 |
| descend_to_place | descend | 1.00 / time_limit | (0.559, 0.087, 0.190)→(0.606, 0.148, 0.168) | (0.567, 0.087, 0.181)→(0.610, 0.144, 0.106) | 0.115→0.094 | 1.00 / 32.000 | 0.086 | 0.652 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 1.000
- terminal_score: 0.801
- phase_score: 0.447
- phase_breakdown.lift_object_score: 0.652
- phase_breakdown.reach_object_score: 0.084
- phase_breakdown.place_goal_score: 0.469
- grasp_place_fitness: 0.863

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.863
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.801
- **Median Q (composite search score)**: -0.209
- **K-run variance**: 0.0079
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01449,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_time":1.35459,"approach_goal.approach_goal_x":-0.00708,"approach_goal.approach_goal_y":0.0424,"approach_goal.approach_goal_z":0.05459,"approach_goal.approach_speed":0.16822,"approach_object.approach_object_time":2.47629,"approach_object.approach_offset_x":0.0292,"approach_object.approach_offset_y":-0.03581,"approach_object.approach_offset_z":0.11787,"descend_to_grasp.descend_grasp_time":2.21529,"descend_to_grasp.descend_grasp_x":0.01946,"descend_to_grasp.descend_grasp_y":0.00635,"descend_to_grasp.descend_grasp_z":-0.01932,"descend_to_place.descend_place_time":4.33518,"descend_to_place.place_x":-0.01151,"descend_to_place.place_y":0.00672,"descend_to_place.place_z":0.0032,"grasp.grasp_time":0.60469,"lift.lift_height":0.21468,"lift.lift_time":3.41},"optimized_scores":{"best_composite_score":-0.13657,"best_fitness_score":0.86343,"best_task_score":0.80079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":572.0,"contact_point_centroid":[0.48524,0.0243,-0.00124],"force_p95":1.97854,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.78934,"mean_force":0.71497,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48492,-0.01525,0.00394]},{"body_a":"world","body_b":"left_finger","contact_count":582.0,"contact_point_centroid":[0.4853,-0.05479,-0.00127],"force_p95":1.87881,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.66263,"mean_force":0.70631,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4849,-0.01526,0.00399]},{"body_a":"world","body_b":"left_finger","contact_count":6448.0,"contact_point_centroid":[0.48614,-0.05659,-0.00201],"force_p95":1.13669,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.14091,"mean_force":0.91197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4866,-0.01524,0.00242]},{"body_a":"world","body_b":"right_finger","contact_count":6424.0,"contact_point_centroid":[0.48608,0.02613,-0.00196],"force_p95":1.11577,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.11978,"mean_force":0.89289,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48658,-0.01524,0.0024]},{"body_a":"world","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.47332,-0.01871,-0.00249],"force_p95":0.31799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0765,"mean_force":0.18472,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48304,-0.01537,0.00858]},{"body_a":"grasp_target","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.49269,-0.02069,0.0468],"force_p95":0.37272,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.6544,"mean_force":0.35488,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48668,-0.01524,0.00251]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.4944,-0.02548,0.1165],"force_p95":0.27406,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55944,"mean_force":0.09456,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47835,-0.01667,0.07731]},{"body_a":"grasp_target","body_b":"hand","contact_count":67.0,"contact_point_centroid":[0.49603,-0.03943,0.05312],"force_p95":0.31428,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37295,"mean_force":0.22994,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49123,-0.01667,0.01221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18268.0,"contact_point_centroid":[0.47804,-0.03603,0.08594],"force_p95":0.07094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30633,"mean_force":0.05042,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47782,-0.0168,0.08408]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47393,-0.01961,-0.00333],"force_p95":0.27762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28693,"mean_force":0.20905,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48668,-0.01524,0.00251]},{"body_a":"world","body_b":"grasp_target","contact_count":3184.0,"contact_point_centroid":[0.47615,-0.02014,-0.00203],"force_p95":0.1693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25651,"mean_force":0.12687,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49429,-0.03355,0.07332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17748.0,"contact_point_centroid":[0.4779,0.00228,0.08809],"force_p95":0.06933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1888,"mean_force":0.04857,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47771,-0.01684,0.08617]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49947,-0.02727,0.22063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.50655,0.0137,0.17521],"force_p95":0.07109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09047,"mean_force":0.04932,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5063,0.03284,0.17334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20272.0,"contact_point_centroid":[0.56939,0.09802,0.18857],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08866,"mean_force":0.04862,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56989,0.11722,0.18627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21515.0,"contact_point_centroid":[0.56912,0.13575,0.18852],"force_p95":0.06819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08861,"mean_force":0.04625,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56929,0.11662,0.18627]}],"total_contact_groups":18},"final_pose_error":0.03232,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60384,0.14491,0.17793],"final_tcp_position":[0.59671,0.14491,0.18513],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.78934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50118,-0.05334,0.1486],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12943,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.47602,-0.01938,0.02402],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28913,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.31624,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3251.0,"raw_peak_contact_force":0.37295,"subtask_id":"reach_object","tcp_end":[0.49092,-0.01534,0.0074],"tcp_start":[0.50118,-0.05334,0.1486],"tcp_to_object_dist_end":0.02268,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47592,-0.01964,0.02315],"object_pos_start":[0.47602,-0.01938,0.02402],"object_to_goal_dist_end":0.28983,"object_to_goal_dist_start":0.28913,"object_z_max":0.02402,"peak_contact_force":1.14091,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15622.0,"raw_peak_contact_force":1.14091,"tcp_end":[0.48578,-0.01525,0.00171],"tcp_start":[0.4858,-0.01525,0.00172],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47923,-0.01819,0.16679],"object_pos_start":[0.47579,-0.01964,0.02315],"object_to_goal_dist_end":0.23487,"object_to_goal_dist_start":0.28991,"object_z_max":0.1666,"peak_contact_force":0.06989,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38690.0,"raw_peak_contact_force":2.78934,"subtask_id":"lift_object","tcp_end":[0.47503,-0.01817,0.15875],"tcp_start":[0.48578,-0.01525,0.00171],"tcp_to_object_dist_end":0.00908,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55222,0.08664,0.19301],"object_pos_start":[0.47923,-0.01819,0.16679],"object_to_goal_dist_end":0.10745,"object_to_goal_dist_start":0.23487,"object_z_max":0.19299,"peak_contact_force":0.07781,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40092.0,"raw_peak_contact_force":0.09047,"subtask_id":"place_goal","tcp_end":[0.54297,0.08653,0.19336],"tcp_start":[0.47503,-0.01817,0.15875],"tcp_to_object_dist_end":0.00925,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60384,0.14491,0.17793],"object_pos_start":[0.55222,0.08664,0.19301],"object_to_goal_dist_end":0.03332,"object_to_goal_dist_start":0.10745,"object_z_max":0.19301,"peak_contact_force":0.0676,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":41787.0,"raw_peak_contact_force":0.08866,"subtask_id":"place_goal","tcp_end":[0.59671,0.14491,0.18513],"tcp_start":[0.54297,0.08653,0.19336],"tcp_to_object_dist_end":0.01014,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01504,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_time":3.37715,"approach_goal.approach_goal_x":-0.0106,"approach_goal.approach_goal_y":0.00083,"approach_goal.approach_goal_z":0.05233,"approach_goal.approach_speed":0.17687,"approach_object.approach_object_time":2.59757,"approach_object.approach_offset_x":-0.0087,"approach_object.approach_offset_y":0.01209,"approach_object.approach_offset_z":0.0794,"descend_to_grasp.descend_grasp_time":3.63236,"descend_to_grasp.descend_grasp_x":0.01841,"descend_to_grasp.descend_grasp_y":-0.00255,"descend_to_grasp.descend_grasp_z":-0.01057,"descend_to_place.descend_place_time":3.54524,"descend_to_place.place_x":0.01558,"descend_to_place.place_y":0.02995,"descend_to_place.place_z":0.00228,"grasp.grasp_time":0.77816,"lift.lift_height":0.22572,"lift.lift_time":2.10023},"optimized_scores":{"best_composite_score":-0.20869,"best_fitness_score":0.79131,"best_task_score":0.61302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":327.0,"contact_point_centroid":[0.45467,-0.02634,-0.00163],"force_p95":0.40362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93917,"mean_force":0.14001,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45842,-0.02629,0.01784]},{"body_a":"grasp_target","body_b":"hand","contact_count":348.0,"contact_point_centroid":[0.47396,-0.03402,0.07419],"force_p95":0.08839,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3558,"mean_force":0.04126,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4567,-0.02623,0.03603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45621,-0.00709,0.09103],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26792,"mean_force":0.04919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.456,-0.02622,0.0891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45622,-0.04537,0.09095],"force_p95":0.07056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26625,"mean_force":0.04942,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.456,-0.02622,0.0891]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45841,-0.02633,-0.00213],"force_p95":0.14068,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14458,"mean_force":0.13177,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46201,-0.02642,0.0177]},{"body_a":"world","body_b":"grasp_target","contact_count":3240.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47314,-0.00671,0.20549]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45747,-0.02047,0.06418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18804.0,"contact_point_centroid":[0.48947,0.00929,0.16725],"force_p95":0.07659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09803,"mean_force":0.05303,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49016,0.02852,0.16532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":22000.0,"contact_point_centroid":[0.55388,0.14113,0.14804],"force_p95":0.06716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09735,"mean_force":0.04474,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55411,0.12198,0.14571]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20748.0,"contact_point_centroid":[0.55467,0.10407,0.14747],"force_p95":0.06978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09626,"mean_force":0.04689,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55509,0.12329,0.14523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.46105,-0.00718,0.01853],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08951,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46087,-0.02638,0.01661]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4858.0,"contact_point_centroid":[0.46107,-0.04557,0.01847],"force_p95":0.0678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08497,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46087,-0.02638,0.01661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21508.0,"contact_point_centroid":[0.49167,0.05015,0.16752],"force_p95":0.07086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08392,"mean_force":0.04669,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49195,0.0311,0.1652]},{"body_a":"grasp_target","body_b":"hand","contact_count":349.0,"contact_point_centroid":[0.47796,-0.02887,0.05517],"force_p95":0.04472,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06704,"mean_force":0.03965,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46105,-0.02638,0.01679]}],"total_contact_groups":14},"final_pose_error":0.10966,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.58163,0.15381,0.12285],"final_tcp_position":[0.57812,0.15377,0.13468],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.93917,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":811.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3240.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.44832,-0.01348,0.11394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08945,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4685,-0.02665,0.02399],"tcp_start":[0.44832,-0.01348,0.11394],"tcp_to_object_dist_end":0.01014,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45813,-0.02639,0.02559],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30407,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13717,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11871.0,"raw_peak_contact_force":0.14458,"tcp_end":[0.46084,-0.02638,0.01658],"tcp_start":[0.4685,-0.02665,0.02399],"tcp_to_object_dist_end":0.00941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46619,-0.02624,0.17495],"object_pos_start":[0.45813,-0.02639,0.02559],"object_to_goal_dist_end":0.29248,"object_to_goal_dist_start":0.30407,"object_z_max":0.17476,"peak_contact_force":0.07288,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40675.0,"raw_peak_contact_force":0.93917,"subtask_id":"lift_object","tcp_end":[0.45529,-0.02622,0.1716],"tcp_start":[0.46084,-0.02638,0.01658],"tcp_to_object_dist_end":0.0114,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53854,0.08925,0.15561],"object_pos_start":[0.46619,-0.02624,0.17495],"object_to_goal_dist_end":0.15577,"object_to_goal_dist_start":0.29248,"object_z_max":0.17506,"peak_contact_force":0.07782,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40312.0,"raw_peak_contact_force":0.09803,"subtask_id":"place_goal","tcp_end":[0.53254,0.08928,0.16283],"tcp_start":[0.45529,-0.02622,0.1716],"tcp_to_object_dist_end":0.00939,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58163,0.15381,0.12285],"object_pos_start":[0.53854,0.08925,0.15561],"object_to_goal_dist_end":0.0734,"object_to_goal_dist_start":0.15577,"object_z_max":0.15561,"peak_contact_force":0.06653,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":42748.0,"raw_peak_contact_force":0.09735,"subtask_id":"place_goal","tcp_end":[0.57812,0.15377,0.13468],"tcp_start":[0.53254,0.08928,0.16283],"tcp_to_object_dist_end":0.01234,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88636,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_time":2.95074,"approach_goal.approach_goal_x":0.02553,"approach_goal.approach_goal_y":0.00748,"approach_goal.approach_goal_z":0.07373,"approach_goal.approach_speed":0.13978,"approach_object.approach_object_time":1.76537,"approach_object.approach_offset_x":-0.02419,"approach_object.approach_offset_y":0.01353,"approach_object.approach_offset_z":0.08286,"descend_to_grasp.descend_grasp_time":4.38759,"descend_to_grasp.descend_grasp_x":0.01936,"descend_to_grasp.descend_grasp_y":0.00405,"descend_to_grasp.descend_grasp_z":-0.00106,"descend_to_place.descend_place_time":2.41287,"descend_to_place.place_x":0.00572,"descend_to_place.place_y":-0.00402,"descend_to_place.place_z":-0.00086,"grasp.grasp_time":0.59253,"lift.lift_height":0.20016,"lift.lift_time":2.05893},"optimized_scores":{"best_composite_score":-0.35017,"best_fitness_score":0.64983,"best_task_score":0.30777},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1450.0,"contact_point_centroid":[0.64576,0.13391,-0.00271],"force_p95":0.35017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76972,"mean_force":0.15336,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6364,0.13515,0.18703]},{"body_a":"world","body_b":"grasp_target","contact_count":293.0,"contact_point_centroid":[0.54057,0.00705,-0.00193],"force_p95":0.43107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83974,"mean_force":0.12631,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53928,0.00617,0.0254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19795.0,"contact_point_centroid":[0.53862,-0.01307,0.09828],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34796,"mean_force":0.05119,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53833,0.00607,0.09629]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00206,-0.00256],"force_p95":0.26391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33797,"mean_force":0.16449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54313,0.00628,0.0246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19704.0,"contact_point_centroid":[0.53859,0.02523,0.09797],"force_p95":0.07891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31136,"mean_force":0.0502,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53832,0.00607,0.09607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.61464,0.08038,0.19861],"force_p95":0.16331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26842,"mean_force":0.10097,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6103,0.0992,0.20045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7804.0,"contact_point_centroid":[0.61531,0.11944,0.19854],"force_p95":0.10241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24793,"mean_force":0.06425,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61192,0.10149,0.19948]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14490.0,"contact_point_centroid":[0.56816,0.02168,0.19208],"force_p95":0.10944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16048,"mean_force":0.07129,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56547,0.04066,0.19067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4522.0,"contact_point_centroid":[0.54202,0.02547,0.02508],"force_p95":0.08941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13846,"mean_force":0.04699,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54184,0.00624,0.02309]},{"body_a":"world","body_b":"grasp_target","contact_count":3912.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50675,0.0073,0.20083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16370.0,"contact_point_centroid":[0.56949,0.06088,0.19227],"force_p95":0.0877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12616,"mean_force":0.06037,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56672,0.04217,0.19142]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53183,0.01004,0.06878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5324.0,"contact_point_centroid":[0.5421,-0.01358,0.02498],"force_p95":0.09053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09902,"mean_force":0.04596,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54187,0.00624,0.02312]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1291.0,"contact_point_centroid":[0.63825,0.137,0.1886],"force_p95":0.01186,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63774,0.13698,0.1864]}],"total_contact_groups":14},"final_pose_error":0.01359,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64581,0.13388,0.01602],"final_tcp_position":[0.64466,0.14643,0.18309],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.76972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3912.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51516,0.01406,0.11293],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09258,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55043,0.00652,0.03329],"tcp_start":[0.51516,0.01406,0.11293],"tcp_to_object_dist_end":0.01093,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54408,0.00608,0.024],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24849,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.23726,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11646.0,"raw_peak_contact_force":0.33797,"tcp_end":[0.54182,0.00625,0.02306],"tcp_start":[0.55043,0.00652,0.03329],"tcp_to_object_dist_end":0.00245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55263,0.00592,0.1738],"object_pos_start":[0.54408,0.00608,0.024],"object_to_goal_dist_end":0.18021,"object_to_goal_dist_start":0.24849,"object_z_max":0.17362,"peak_contact_force":0.08117,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39792.0,"raw_peak_contact_force":0.83974,"subtask_id":"lift_object","tcp_end":[0.5397,0.00601,0.17826],"tcp_start":[0.54182,0.00625,0.02306],"tcp_to_object_dist_end":0.01368,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61021,0.08386,0.19355],"object_pos_start":[0.55263,0.00592,0.1738],"object_to_goal_dist_end":0.08316,"object_to_goal_dist_start":0.18021,"object_z_max":0.19353,"peak_contact_force":0.11315,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30860.0,"raw_peak_contact_force":0.16048,"subtask_id":"place_goal","tcp_end":[0.60181,0.08385,0.21291],"tcp_start":[0.5397,0.00601,0.17826],"tcp_to_object_dist_end":0.0211,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64581,0.13388,0.01602],"object_pos_start":[0.61021,0.08386,0.19355],"object_to_goal_dist_end":0.17676,"object_to_goal_dist_start":0.08316,"object_z_max":0.19355,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15641.0,"raw_peak_contact_force":1.76972,"subtask_id":"place_goal","tcp_end":[0.64466,0.14643,0.18309],"tcp_start":[0.60181,0.08385,0.21291],"tcp_to_object_dist_end":0.16755,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```