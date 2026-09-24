## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1377 | 0.95 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | -0.2318 | 0.57 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | time_limit | time_limit | time_limit | 20  | 0.1407 | 0.96 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1660 | 1.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.0240 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.024) — your mutation base

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

- **Composite score**: 0.024
- **task_score** (E): 1.000
- **fitness_score**: 0.994  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.970

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1695 |
| descend_to_grasp | 1.00 | 1.00 | 0.1076 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 1.00 | 1.00 | 0.1619 |
| approach_goal | 1.00 | 1.00 | 0.2318 |
| descend_to_place | 1.00 | 1.00 | 0.0419 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, -0.012, 0.137) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, -0.012, 0.137)→(0.500, -0.012, 0.033) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.500, -0.012, 0.033)→(0.492, -0.012, 0.025) | (0.493, -0.015, 0.026)→(0.493, -0.012, 0.024) | 0.281→0.279 | 1.00 / 44.000 | 0.233 | 0.335 |
| lift | lift | 1.00 / step_budget | (0.492, -0.012, 0.025)→(0.489, -0.012, 0.186) | (0.493, -0.012, 0.024)→(0.502, -0.012, 0.180) | 0.279→0.233 | 1.00 / 37.000 | 0.089 | 0.802 |
| approach_goal | approach | 1.00 / step_budget | (0.489, -0.012, 0.186)→(0.639, 0.159, 0.209) | (0.502, -0.012, 0.180)→(0.645, 0.159, 0.192) | 0.233→0.040 | 1.00 / 37.333 | 0.063 | 0.141 |
| descend_to_place | descend | 1.00 / step_budget | (0.639, 0.159, 0.209)→(0.638, 0.171, 0.175) | (0.645, 0.159, 0.192)→(0.641, 0.170, 0.158) | 0.040→0.017 | 1.00 / 36.000 | 0.086 | 0.216 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.218
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.678
- phase_breakdown.lift_object_score: 0.844
- phase_breakdown.reach_object_score: 0.150
- phase_breakdown.place_goal_score: 0.789
- grasp_place_fitness: 0.995

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.995
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.023
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86243,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_tolerance":0.02658,"approach_goal.approach_goal_x":0.03499,"approach_goal.approach_goal_y":0.00295,"approach_goal.approach_goal_z":0.05836,"approach_goal.approach_speed":0.07659,"approach_object.approach_offset_x":-0.00699,"approach_object.approach_offset_y":-0.00742,"approach_object.approach_offset_z":0.09357,"descend_to_grasp.descend_grasp_x":0.01419,"descend_to_grasp.descend_grasp_y":-0.00243,"descend_to_grasp.descend_grasp_z":-0.00729,"descend_to_place.place_speed":0.1158,"descend_to_place.place_tolerance":0.03618,"descend_to_place.place_x":-0.00293,"descend_to_place.place_y":-0.00681,"descend_to_place.place_z":-0.00717,"lift.lift_height":0.19209},"optimized_scores":{"best_composite_score":0.02332,"best_fitness_score":0.99332,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.47315,-0.02405,-0.00141],"force_p95":0.48098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69473,"mean_force":0.08013,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47207,-0.02268,0.03052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19204.0,"contact_point_centroid":[0.47115,-0.00336,0.10906],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32883,"mean_force":0.05239,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47074,-0.02249,0.10695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19799.0,"contact_point_centroid":[0.4712,-0.0416,0.11036],"force_p95":0.07538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30385,"mean_force":0.05052,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47077,-0.02248,0.10849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.65073,0.17126,0.22028],"force_p95":0.15029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28814,"mean_force":0.0948,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64709,0.15236,0.2197]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02052,-0.00228],"force_p95":0.19386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27164,"mean_force":0.14311,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47479,-0.02276,0.02946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.65021,0.13393,0.21988],"force_p95":0.11523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20829,"mean_force":0.07294,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64707,0.15236,0.21965]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10505.0,"contact_point_centroid":[0.56315,0.08218,0.21262],"force_p95":0.11297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1797,"mean_force":0.07921,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55995,0.06323,0.21166]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4727.0,"contact_point_centroid":[0.47384,-0.04192,0.03017],"force_p95":0.07762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15639,"mean_force":0.04508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47364,-0.02273,0.0283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13059.0,"contact_point_centroid":[0.56425,0.04626,0.2124],"force_p95":0.08912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13968,"mean_force":0.06074,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56155,0.06475,0.21206]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48339,-0.01229,0.21666]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47388,-0.02388,0.07742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5125.0,"contact_point_centroid":[0.47383,-0.00334,0.03027],"force_p95":0.07862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08622,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47365,-0.02273,0.02831]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.64384,0.15162,0.17987],"final_tcp_position":[0.63827,0.15193,0.20022],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.69473,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46803,-0.02517,0.13313],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48132,-0.02295,0.0361],"tcp_start":[0.46803,-0.02517,0.13313],"tcp_to_object_dist_end":0.01167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47601,-0.02246,0.025],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29048,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.18162,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11652.0,"raw_peak_contact_force":0.27164,"tcp_end":[0.47361,-0.02273,0.02827],"tcp_start":[0.48132,-0.02295,0.0361],"tcp_to_object_dist_end":0.00406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48562,-0.02225,0.18167],"object_pos_start":[0.47601,-0.02246,0.025],"object_to_goal_dist_end":0.23292,"object_to_goal_dist_start":0.29048,"object_z_max":0.18149,"peak_contact_force":0.09364,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39152.0,"raw_peak_contact_force":0.69473,"subtask_id":"lift_object","tcp_end":[0.47214,-0.02237,0.19167],"tcp_start":[0.47361,-0.02273,0.02827],"tcp_to_object_dist_end":0.01678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.66465,0.15241,0.21782],"object_pos_start":[0.48562,-0.02225,0.18167],"object_to_goal_dist_end":0.04386,"object_to_goal_dist_start":0.23292,"object_z_max":0.21779,"peak_contact_force":0.11821,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23564.0,"raw_peak_contact_force":0.1797,"subtask_id":"place_goal","tcp_end":[0.65405,0.15232,0.23618],"tcp_start":[0.47214,-0.02237,0.19167],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.64384,0.15162,0.17987],"object_pos_start":[0.66465,0.15241,0.21782],"object_to_goal_dist_end":0.01773,"object_to_goal_dist_start":0.04386,"object_z_max":0.21782,"peak_contact_force":0.10236,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.28814,"subtask_id":"place_goal","tcp_end":[0.63827,0.15193,0.20022],"tcp_start":[0.65405,0.15232,0.23618],"tcp_to_object_dist_end":0.0211,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01282,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_tolerance":0.03641,"approach_goal.approach_goal_x":0.02816,"approach_goal.approach_goal_y":-0.00516,"approach_goal.approach_goal_z":0.05975,"approach_goal.approach_speed":0.16793,"approach_object.approach_offset_x":0.04996,"approach_object.approach_offset_y":-0.01357,"approach_object.approach_offset_z":0.10716,"descend_to_grasp.descend_grasp_x":0.00669,"descend_to_grasp.descend_grasp_y":0.00851,"descend_to_grasp.descend_grasp_z":-0.00319,"descend_to_place.place_speed":0.14189,"descend_to_place.place_tolerance":0.02371,"descend_to_place.place_x":-0.00597,"descend_to_place.place_y":-0.01638,"descend_to_place.place_z":0.00342,"lift.lift_height":0.19353},"optimized_scores":{"best_composite_score":0.02318,"best_fitness_score":0.99318,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.4551,-0.01608,-0.00191],"force_p95":0.59641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87333,"mean_force":0.1105,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45415,-0.01885,0.02323]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02471,-0.00274],"force_p95":0.31673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39328,"mean_force":0.1812,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45705,-0.01891,0.02103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19309.0,"contact_point_centroid":[0.45355,-0.03792,0.10039],"force_p95":0.08401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35175,"mean_force":0.05339,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45304,-0.01877,0.0984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19474.0,"contact_point_centroid":[0.45351,0.00038,0.1009],"force_p95":0.08474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31418,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45305,-0.01877,0.09896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1385.0,"contact_point_centroid":[0.63907,0.21032,0.15449],"force_p95":0.09137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22748,"mean_force":0.05157,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63947,0.19121,0.152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.63854,0.1719,0.15436],"force_p95":0.0873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17793,"mean_force":0.05681,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63949,0.19121,0.15205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14717.0,"contact_point_centroid":[0.5577,0.11437,0.17313],"force_p95":0.08423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14846,"mean_force":0.05115,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.557,0.09541,0.17164]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50101,-0.01781,0.22234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13417.0,"contact_point_centroid":[0.55441,0.07273,0.17341],"force_p95":0.08949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13432,"mean_force":0.05698,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55377,0.09188,0.17189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.45596,0.00043,0.02254],"force_p95":0.09931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12871,"mean_force":0.05147,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45594,-0.0189,0.01997]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48265,-0.02783,0.08507]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5461.0,"contact_point_centroid":[0.45622,-0.03934,0.02165],"force_p95":0.10039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11359,"mean_force":0.04835,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45598,-0.0189,0.02001]}],"total_contact_groups":12},"final_pose_error":0.01945,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62757,0.19074,0.11259],"final_tcp_position":[0.63223,0.19083,0.1352],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.87333,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50406,-0.03638,0.1451],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46361,-0.01907,0.0273],"tcp_start":[0.50406,-0.03638,0.1451],"tcp_to_object_dist_end":0.00892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4583,-0.01885,0.02335],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29887,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.27563,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11369.0,"raw_peak_contact_force":0.39328,"tcp_end":[0.45592,-0.01888,0.01995],"tcp_start":[0.46361,-0.01907,0.0273],"tcp_to_object_dist_end":0.00415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46982,-0.01871,0.1774],"object_pos_start":[0.4583,-0.01885,0.02335],"object_to_goal_dist_end":0.28496,"object_to_goal_dist_start":0.29887,"object_z_max":0.17722,"peak_contact_force":0.09745,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38966.0,"raw_peak_contact_force":0.87333,"subtask_id":"lift_object","tcp_end":[0.45431,-0.01875,0.18216],"tcp_start":[0.45592,-0.01888,0.01995],"tcp_to_object_dist_end":0.01623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.64253,0.1911,0.14382],"object_pos_start":[0.46982,-0.01871,0.1774],"object_to_goal_dist_end":0.03645,"object_to_goal_dist_start":0.28496,"object_z_max":0.17749,"peak_contact_force":0.07186,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28134.0,"raw_peak_contact_force":0.14846,"subtask_id":"place_goal","tcp_end":[0.64491,0.19104,0.16523],"tcp_start":[0.45431,-0.01875,0.18216],"tcp_to_object_dist_end":0.02154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.62757,0.19074,0.11259],"object_pos_start":[0.64253,0.1911,0.14382],"object_to_goal_dist_end":0.01773,"object_to_goal_dist_start":0.03645,"object_z_max":0.14382,"peak_contact_force":0.0779,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2533.0,"raw_peak_contact_force":0.22748,"subtask_id":"place_goal","tcp_end":[0.63223,0.19083,0.1352],"tcp_start":[0.64491,0.19104,0.16523],"tcp_to_object_dist_end":0.02309,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_tolerance":0.03328,"approach_goal.approach_goal_x":-0.01943,"approach_goal.approach_goal_y":-0.01145,"approach_goal.approach_goal_z":0.04611,"approach_goal.approach_speed":0.06164,"approach_object.approach_offset_x":0.00941,"approach_object.approach_offset_y":0.02625,"approach_object.approach_offset_z":0.09724,"descend_to_grasp.descend_grasp_x":0.01969,"descend_to_grasp.descend_grasp_y":0.00124,"descend_to_grasp.descend_grasp_z":-0.00826,"descend_to_place.place_speed":0.07213,"descend_to_place.place_tolerance":0.03932,"descend_to_place.place_x":0.00836,"descend_to_place.place_y":0.02529,"descend_to_place.place_z":-0.00247,"lift.lift_height":0.19798},"optimized_scores":{"best_composite_score":0.02536,"best_fitness_score":0.99536,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":211.0,"contact_point_centroid":[0.54088,0.00822,-0.00182],"force_p95":0.54556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83866,"mean_force":0.10702,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54407,0.00672,0.02831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54125,-0.01264,0.10584],"force_p95":0.07811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37596,"mean_force":0.05018,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54101,0.0065,0.10389]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54418,0.00206,-0.0026],"force_p95":0.27183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33966,"mean_force":0.1672,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54766,0.00683,0.02694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.54123,0.02568,0.10571],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33215,"mean_force":0.04876,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54101,0.0065,0.10389]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52176,0.0125,0.21542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4509.0,"contact_point_centroid":[0.54655,0.02604,0.02743],"force_p95":0.09109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13467,"mean_force":0.04728,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54637,0.00679,0.02541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2244.0,"contact_point_centroid":[0.63049,0.17047,0.20928],"force_p95":0.0818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13274,"mean_force":0.05656,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62982,0.1513,0.20703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2390.0,"contact_point_centroid":[0.6299,0.13148,0.21002],"force_p95":0.08026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12998,"mean_force":0.05379,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62923,0.15048,0.20784]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54919,0.01521,0.07715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5339.0,"contact_point_centroid":[0.54662,-0.01312,0.02724],"force_p95":0.09277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10022,"mean_force":0.04618,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5464,0.00679,0.02544]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10400.0,"contact_point_centroid":[0.57934,0.05307,0.20523],"force_p95":0.07289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09336,"mean_force":0.04946,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57907,0.0722,0.20327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10390.0,"contact_point_centroid":[0.57929,0.09129,0.20507],"force_p95":0.07295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07962,"mean_force":0.04897,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57904,0.07214,0.20325]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65297,0.1686,0.18083],"final_tcp_position":[0.64257,0.16879,0.19047],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.83866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.54598,0.02526,0.13289],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55503,0.0071,0.03582],"tcp_start":[0.54598,0.02526,0.13289],"tcp_to_object_dist_end":0.01571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54402,0.00639,0.02386],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24843,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.24147,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11648.0,"raw_peak_contact_force":0.33966,"tcp_end":[0.54635,0.0068,0.02538],"tcp_start":[0.55503,0.0071,0.03582],"tcp_to_object_dist_end":0.00281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54961,0.00624,0.17982],"object_pos_start":[0.54402,0.00639,0.02386],"object_to_goal_dist_end":0.18108,"object_to_goal_dist_start":0.24843,"object_z_max":0.17964,"peak_contact_force":0.07707,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40211.0,"raw_peak_contact_force":0.83866,"subtask_id":"lift_object","tcp_end":[0.5405,0.00635,0.18548],"tcp_start":[0.54635,0.0068,0.02538],"tcp_to_object_dist_end":0.01072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.62657,0.1348,0.21539],"object_pos_start":[0.54961,0.00624,0.17982],"object_to_goal_dist_end":0.03969,"object_to_goal_dist_start":0.18108,"object_z_max":0.21533,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20790.0,"raw_peak_contact_force":0.09336,"subtask_id":"place_goal","tcp_end":[0.61832,0.13489,0.22467],"tcp_start":[0.5405,0.00635,0.18548],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.65297,0.1686,0.18083],"object_pos_start":[0.62657,0.1348,0.21539],"object_to_goal_dist_end":0.01564,"object_to_goal_dist_start":0.03969,"object_z_max":0.21539,"peak_contact_force":0.07701,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4634.0,"raw_peak_contact_force":0.13274,"subtask_id":"place_goal","tcp_end":[0.64257,0.16879,0.19047],"tcp_start":[0.61832,0.13489,0.22467],"tcp_to_object_dist_end":0.01418,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```