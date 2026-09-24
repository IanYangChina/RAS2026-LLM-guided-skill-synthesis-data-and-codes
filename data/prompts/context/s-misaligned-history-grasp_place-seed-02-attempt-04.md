## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2015 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | 0.1073 | 0.16 | ❌ rejected |
| 2 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1073 | 0.16 | ❌ rejected |
| 1 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1073 | 0.16 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0  | 0.1129 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.894, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.113) — your mutation base

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
  control: impedance_control
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

- **Composite score**: 0.113
- **task_score** (E): 0.894
- **fitness_score**: 0.933  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1640 |
| descend_to_grasp | 1.00 | 1.00 | 0.1189 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 1.00 | 1.00 | 0.1582 |
| approach_goal | 0.00 | 1.00 | 0.1447 |
| descend_to_place | 1.00 | 1.00 | 0.1035 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, -0.001, 0.140) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.507, -0.001, 0.140)→(0.504, -0.003, 0.024) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.504, -0.003, 0.024)→(0.496, -0.003, 0.016) | (0.493, -0.015, 0.026)→(0.492, -0.003, 0.023) | 0.281→0.275 | 1.00 / 45.000 | 0.258 | 0.414 |
| lift | lift | 1.00 / step_budget | (0.496, -0.003, 0.016)→(0.489, -0.003, 0.174) | (0.492, -0.003, 0.023)→(0.499, -0.003, 0.176) | 0.275→0.229 | 1.00 / 40.000 | 0.076 | 1.096 |
| approach_goal | approach | 0.00 / step_budget | (0.489, -0.003, 0.174)→(0.581, 0.091, 0.219) | (0.499, -0.003, 0.176)→(0.586, 0.091, 0.210) | 0.229→0.109 | 1.00 / 40.333 | 0.072 | 0.097 |
| descend_to_place | descend | 1.00 / step_budget | (0.581, 0.091, 0.219)→(0.628, 0.163, 0.166) | (0.586, 0.091, 0.210)→(0.631, 0.163, 0.153) | 0.109→0.024 | 1.00 / 39.667 | 0.072 | 0.122 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.006
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.650
- phase_breakdown.lift_object_score: 0.678
- phase_breakdown.reach_object_score: 0.124
- phase_breakdown.place_goal_score: 0.844
- grasp_place_fitness: 0.989

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.989
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.353


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02158,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.02009,"approach_goal.approach_goal_y":-0.04999,"approach_goal.approach_goal_z":0.07979,"approach_goal.approach_speed":0.17046,"approach_object.approach_offset_x":0.04787,"approach_object.approach_offset_y":0.01874,"approach_object.approach_offset_z":0.09077,"descend_to_grasp.descend_grasp_x":0.01388,"descend_to_grasp.descend_grasp_y":0.01783,"descend_to_grasp.descend_grasp_z":-0.00839,"descend_to_place.place_x":0.0074,"descend_to_place.place_y":-0.02566,"descend_to_place.place_z":0.00671,"lift.lift_height":0.20326},"optimized_scores":{"best_composite_score":0.06996,"best_fitness_score":0.88996,"best_task_score":0.8122},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":222.0,"contact_point_centroid":[0.47194,-0.00022,-0.00209],"force_p95":0.79067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14278,"mean_force":0.13875,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47741,-0.00241,0.01757]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47504,-0.01292,-0.00316],"force_p95":0.44764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46589,"mean_force":0.25785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48082,-0.00243,0.01508]},{"body_a":"grasp_target","body_b":"hand","contact_count":387.0,"contact_point_centroid":[0.49147,-0.01982,0.08227],"force_p95":0.08213,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45992,"mean_force":0.04675,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47479,-0.00235,0.04399]},{"body_a":"grasp_target","body_b":"hand","contact_count":388.0,"contact_point_centroid":[0.49431,-0.02518,0.05346],"force_p95":0.36517,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37543,"mean_force":0.18482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48009,-0.00245,0.01435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47377,-0.02136,0.096],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33042,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47354,-0.00221,0.09407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47375,0.01697,0.09591],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27878,"mean_force":0.0486,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47354,-0.00221,0.09407]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50796,-0.00066,0.21409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7068.0,"contact_point_centroid":[0.48007,-0.02821,0.01611],"force_p95":0.10318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13499,"mean_force":0.05948,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47986,-0.00246,0.01413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14540.0,"contact_point_centroid":[0.60586,0.08966,0.2086],"force_p95":0.06942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13044,"mean_force":0.0487,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60554,0.10879,0.20664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14540.0,"contact_point_centroid":[0.60578,0.12793,0.20844],"force_p95":0.07111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12941,"mean_force":0.04887,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60554,0.10879,0.20664]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50174,-0.00182,0.07433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2795.0,"contact_point_centroid":[0.47979,0.01664,0.01619],"force_p95":0.09228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10696,"mean_force":0.04788,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47963,-0.00245,0.01389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.52168,0.02066,0.20762],"force_p95":0.07057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09277,"mean_force":0.049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52141,0.0398,0.20571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.52164,0.05894,0.20756],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08715,"mean_force":0.04886,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52141,0.0398,0.20571]}],"total_contact_groups":14},"final_pose_error":0.01008,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63612,0.13106,0.17735],"final_tcp_position":[0.63304,0.13109,0.18884],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.14278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.51826,-0.00134,0.12875],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48769,-0.00229,0.02199],"tcp_start":[0.51826,-0.00134,0.12875],"tcp_to_object_dist_end":0.02164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4745,-0.00185,0.02247],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28041,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.29515,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12051.0,"raw_peak_contact_force":0.46589,"tcp_end":[0.47962,-0.0024,0.01389],"tcp_start":[0.48769,-0.00229,0.02199],"tcp_to_object_dist_end":0.01001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48035,-0.00194,0.17938],"object_pos_start":[0.4745,-0.00185,0.02247],"object_to_goal_dist_end":0.22113,"object_to_goal_dist_start":0.28041,"object_z_max":0.17919,"peak_contact_force":0.07622,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40609.0,"raw_peak_contact_force":1.14278,"subtask_id":"lift_object","tcp_end":[0.47183,-0.00198,0.17591],"tcp_start":[0.47962,-0.0024,0.01389],"tcp_to_object_dist_end":0.0092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57454,0.0784,0.22871],"object_pos_start":[0.48035,-0.00194,0.17938],"object_to_goal_dist_end":0.10611,"object_to_goal_dist_start":0.22113,"object_z_max":0.22868,"peak_contact_force":0.07027,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.09277,"subtask_id":"place_goal","tcp_end":[0.57003,0.07836,0.23697],"tcp_start":[0.47183,-0.00198,0.17591],"tcp_to_object_dist_end":0.00941,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.63612,0.13106,0.17735],"object_pos_start":[0.57454,0.0784,0.22871],"object_to_goal_dist_end":0.0312,"object_to_goal_dist_start":0.10611,"object_z_max":0.22871,"peak_contact_force":0.07056,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29080.0,"raw_peak_contact_force":0.13044,"subtask_id":"place_goal","tcp_end":[0.63304,0.13109,0.18884],"tcp_start":[0.57003,0.07836,0.23697],"tcp_to_object_dist_end":0.0119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03425,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.02014,"approach_goal.approach_goal_y":0.00223,"approach_goal.approach_goal_z":0.07846,"approach_goal.approach_speed":0.17337,"approach_object.approach_offset_x":0.00425,"approach_object.approach_offset_y":0.02709,"approach_object.approach_offset_z":0.13387,"descend_to_grasp.descend_grasp_x":0.01654,"descend_to_grasp.descend_grasp_y":0.00388,"descend_to_grasp.descend_grasp_z":-0.0111,"descend_to_place.place_x":-0.00771,"descend_to_place.place_y":0.00691,"descend_to_place.place_z":0.01141,"lift.lift_height":0.16996},"optimized_scores":{"best_composite_score":0.09983,"best_fitness_score":0.91983,"best_task_score":0.86845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.45574,-0.01882,-0.00157],"force_p95":0.80594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04392,"mean_force":0.11565,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46003,-0.02016,0.01893]},{"body_a":"grasp_target","body_b":"hand","contact_count":242.0,"contact_point_centroid":[0.47488,-0.03871,0.07293],"force_p95":0.05123,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4387,"mean_force":0.03174,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45772,-0.02007,0.03491]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45833,-0.02408,-0.00248],"force_p95":0.27059,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33743,"mean_force":0.17056,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46295,-0.02025,0.01736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45638,-0.03909,0.09896],"force_p95":0.07497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3089,"mean_force":0.04966,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45616,-0.01994,0.09707]},{"body_a":"grasp_target","body_b":"hand","contact_count":356.0,"contact_point_centroid":[0.47796,-0.03818,0.05495],"force_p95":0.27394,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29558,"mean_force":0.08782,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46202,-0.02023,0.01647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.45636,-0.00079,0.09896],"force_p95":0.0739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27539,"mean_force":0.04885,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45616,-0.01994,0.09707]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.1347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48156,0.00031,0.2376]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46535,-0.0108,0.0901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.58707,0.1409,0.14663],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11151,"mean_force":0.04835,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58678,0.16003,0.14466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.58704,0.17917,0.14645],"force_p95":0.07146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11071,"mean_force":0.0486,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58678,0.16003,0.14466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3979.0,"contact_point_centroid":[0.46197,-0.00112,0.01823],"force_p95":0.0814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1096,"mean_force":0.04566,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4618,-0.02023,0.01625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5524.0,"contact_point_centroid":[0.46203,-0.04057,0.01821],"force_p95":0.08251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10553,"mean_force":0.04925,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46184,-0.02023,0.01629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.50874,0.02801,0.17958],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09973,"mean_force":0.04921,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50848,0.04715,0.1777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.5087,0.06628,0.17958],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0889,"mean_force":0.049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50848,0.04715,0.1777]}],"total_contact_groups":14},"final_pose_error":0.02036,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61113,0.19937,0.11118],"final_tcp_position":[0.60959,0.19942,0.12377],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.04392,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46353,0.00067,0.17376],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46947,-0.02038,0.02367],"tcp_start":[0.46353,0.00067,0.17376],"tcp_to_object_dist_end":0.01264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45818,-0.0199,0.02437],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29943,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.20559,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11659.0,"raw_peak_contact_force":0.33743,"tcp_end":[0.46178,-0.0202,0.01624],"tcp_start":[0.46947,-0.02038,0.02367],"tcp_to_object_dist_end":0.0089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4656,-0.0198,0.18154],"object_pos_start":[0.45818,-0.0199,0.02437],"object_to_goal_dist_end":0.28915,"object_to_goal_dist_start":0.29943,"object_z_max":0.18135,"peak_contact_force":0.0761,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40411.0,"raw_peak_contact_force":1.04392,"subtask_id":"lift_object","tcp_end":[0.45473,-0.0198,0.17924],"tcp_start":[0.46178,-0.0202,0.01624],"tcp_to_object_dist_end":0.01111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56121,0.10573,0.17104],"object_pos_start":[0.4656,-0.0198,0.18154],"object_to_goal_dist_end":0.13599,"object_to_goal_dist_start":0.28915,"object_z_max":0.18166,"peak_contact_force":0.07377,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.09973,"subtask_id":"place_goal","tcp_end":[0.55817,0.10567,0.17969],"tcp_start":[0.45473,-0.0198,0.17924],"tcp_to_object_dist_end":0.00918,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61113,0.19937,0.11118],"object_pos_start":[0.56121,0.10573,0.17104],"object_to_goal_dist_end":0.02116,"object_to_goal_dist_start":0.13599,"object_z_max":0.17104,"peak_contact_force":0.07057,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.11151,"subtask_id":"place_goal","tcp_end":[0.60959,0.19942,0.12377],"tcp_start":[0.55817,0.10567,0.17969],"tcp_to_object_dist_end":0.01268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01493,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.00661,"approach_goal.approach_goal_y":-0.03645,"approach_goal.approach_goal_z":0.09601,"approach_goal.approach_speed":0.15984,"approach_object.approach_offset_x":0.00172,"approach_object.approach_offset_y":-0.00234,"approach_object.approach_offset_z":0.08165,"descend_to_grasp.descend_grasp_x":0.01982,"descend_to_grasp.descend_grasp_y":0.01559,"descend_to_grasp.descend_grasp_z":-0.01022,"descend_to_place.place_x":-0.00057,"descend_to_place.place_y":0.00601,"descend_to_place.place_z":0.00119,"lift.lift_height":0.15533},"optimized_scores":{"best_composite_score":0.16886,"best_fitness_score":0.98886,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":229.0,"contact_point_centroid":[0.54147,0.01529,-0.00201],"force_p95":0.72216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10051,"mean_force":0.13769,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54335,0.01301,0.0197]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54404,0.00538,-0.00283],"force_p95":0.36881,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43727,"mean_force":0.21036,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54708,0.01312,0.01802]},{"body_a":"grasp_target","body_b":"hand","contact_count":233.0,"contact_point_centroid":[0.55944,-0.00443,0.07052],"force_p95":0.06237,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43186,"mean_force":0.03097,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54139,0.01299,0.03278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18660.0,"contact_point_centroid":[0.54075,-0.00601,0.09144],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34739,"mean_force":0.0501,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54052,0.01314,0.08948]},{"body_a":"grasp_target","body_b":"hand","contact_count":342.0,"contact_point_centroid":[0.56352,-0.00439,0.05478],"force_p95":0.31018,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31959,"mean_force":0.11903,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54595,0.01306,0.0167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18660.0,"contact_point_centroid":[0.54075,0.03232,0.09129],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30309,"mean_force":0.04875,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54052,0.01314,0.08948]},{"body_a":"world","body_b":"grasp_target","contact_count":2408.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51816,-0.00058,0.20827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6208.0,"contact_point_centroid":[0.54605,-0.00947,0.0186],"force_p95":0.09997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13479,"mean_force":0.05348,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54586,0.01305,0.01659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10935.0,"contact_point_centroid":[0.62944,0.14607,0.20935],"force_p95":0.06959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12322,"mean_force":0.04894,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62915,0.12694,0.20767]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54541,0.00665,0.0667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3398.0,"contact_point_centroid":[0.5458,0.03222,0.01873],"force_p95":0.09689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11904,"mean_force":0.04853,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54576,0.01305,0.01647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10773.0,"contact_point_centroid":[0.62958,0.10889,0.2089],"force_p95":0.07261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11892,"mean_force":0.04918,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62957,0.12804,0.2069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20851.0,"contact_point_centroid":[0.57807,0.07126,0.20451],"force_p95":0.07119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09926,"mean_force":0.04784,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57811,0.05209,0.20246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20611.0,"contact_point_centroid":[0.57767,0.03261,0.20427],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09533,"mean_force":0.04844,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57777,0.05177,0.20212]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64655,0.15945,0.17129],"final_tcp_position":[0.64176,0.15949,0.18518],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.10051,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2408.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53879,-0.00118,0.11826],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5545,0.01346,0.0268],"tcp_start":[0.53879,-0.00118,0.11826],"tcp_to_object_dist_end":0.01601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54413,0.01354,0.02308],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24461,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.27423,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11748.0,"raw_peak_contact_force":0.43727,"tcp_end":[0.54575,0.0131,0.01646],"tcp_start":[0.5545,0.01346,0.0268],"tcp_to_object_dist_end":0.00684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.54992,0.01338,0.16811],"object_pos_start":[0.54413,0.01354,0.02308],"object_to_goal_dist_end":0.17611,"object_to_goal_dist_start":0.24461,"object_z_max":0.168,"peak_contact_force":0.07669,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37782.0,"raw_peak_contact_force":1.10051,"subtask_id":"lift_object","tcp_end":[0.54027,0.01337,0.16545],"tcp_start":[0.54575,0.0131,0.01646],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62353,0.08783,0.2306],"object_pos_start":[0.54992,0.01338,0.16811],"object_to_goal_dist_end":0.08412,"object_to_goal_dist_start":0.17611,"object_z_max":0.23055,"peak_contact_force":0.07063,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41462.0,"raw_peak_contact_force":0.09926,"subtask_id":"place_goal","tcp_end":[0.61607,0.08777,0.24138],"tcp_start":[0.54027,0.01337,0.16545],"tcp_to_object_dist_end":0.0131,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.64655,0.15945,0.17129],"object_pos_start":[0.62353,0.08783,0.2306],"object_to_goal_dist_end":0.01989,"object_to_goal_dist_start":0.08412,"object_z_max":0.2306,"peak_contact_force":0.07379,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21708.0,"raw_peak_contact_force":0.12322,"subtask_id":"place_goal","tcp_end":[0.64176,0.15949,0.18518],"tcp_start":[0.61607,0.08777,0.24138],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```