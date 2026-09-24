## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1146 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1159 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1076 | 0.90 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.0240 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 17  | 0.1781 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.178) — your mutation base

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
    tolerance: 0.02
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
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - -0.01
    tolerance: 0.02
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
    tolerance: 0.02
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
    tolerance: 0.02
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
    tolerance: 0.02
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, -0.01], tolerance=0.02
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.07], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_x: status=consumed; consumers=target.offset.x (add)
    - approach_goal_y: status=consumed; consumers=target.offset.y (add)
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (add)
    - place_y: status=consumed; consumers=target.offset.y (add)
    - place_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.178
- **task_score** (E): 1.000
- **fitness_score**: 0.998  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1770 |
| descend_to_grasp | 1.00 | 1.00 | 0.0947 |
| grasp | 1.00 | 1.00 | 0.0128 |
| lift | 1.00 | 1.00 | 0.1828 |
| approach_goal | 1.00 | 1.00 | 0.2413 |
| descend_to_place | 1.00 | 1.00 | 0.0407 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, -0.018, 0.127) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.505, -0.018, 0.127)→(0.502, -0.013, 0.034) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.502, -0.013, 0.034)→(0.493, -0.013, 0.025) | (0.493, -0.015, 0.026)→(0.493, -0.013, 0.025) | 0.281→0.280 | 1.00 / 44.000 | 0.198 | 0.253 |
| lift | lift | 1.00 / step_budget | (0.493, -0.013, 0.025)→(0.490, -0.013, 0.207) | (0.493, -0.013, 0.025)→(0.502, -0.013, 0.206) | 0.280→0.238 | 1.00 / 38.000 | 0.080 | 0.793 |
| approach_goal | approach | 1.00 / step_budget | (0.490, -0.013, 0.207)→(0.640, 0.171, 0.224) | (0.502, -0.013, 0.206)→(0.645, 0.171, 0.209) | 0.238→0.051 | 1.00 / 39.333 | 0.079 | 0.129 |
| descend_to_place | descend | 1.00 / step_budget | (0.640, 0.171, 0.224)→(0.635, 0.170, 0.185) | (0.645, 0.171, 0.209)→(0.638, 0.170, 0.169) | 0.051→0.011 | 1.00 / 40.000 | 0.076 | 0.199 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.218
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.465
- phase_breakdown.lift_object_score: 0.489
- phase_breakdown.reach_object_score: 0.140
- phase_breakdown.place_goal_score: 0.581
- grasp_place_fitness: 0.999

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.999
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.179
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.256


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02516,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.01575,"approach_goal.approach_goal_y":-0.00793,"approach_goal.approach_goal_z":0.07236,"approach_goal.approach_speed":0.17565,"approach_object.approach_offset_x":0.0182,"approach_object.approach_offset_y":-0.01152,"approach_object.approach_offset_z":0.0806,"descend_to_grasp.descend_grasp_x":0.01017,"descend_to_grasp.descend_grasp_y":0.00188,"descend_to_grasp.descend_grasp_z":-0.01247,"descend_to_place.place_x":-0.00341,"descend_to_place.place_y":-0.00592,"descend_to_place.place_z":0.00269,"lift.lift_height":0.21278},"optimized_scores":{"best_composite_score":0.177,"best_fitness_score":0.997,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.47285,-0.01971,-0.00139],"force_p95":0.72424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76462,"mean_force":0.17367,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47401,-0.01984,0.02566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11857.0,"contact_point_centroid":[0.47225,-0.00063,0.12183],"force_p95":0.07216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31798,"mean_force":0.05109,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47206,-0.01977,0.11979]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12126.0,"contact_point_centroid":[0.47231,-0.03891,0.12351],"force_p95":0.07202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31386,"mean_force":0.05026,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47207,-0.01977,0.12167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.63237,0.16281,0.23524],"force_p95":0.08353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16853,"mean_force":0.05474,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63214,0.14369,0.2334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.63243,0.12453,0.23532],"force_p95":0.08216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15602,"mean_force":0.05359,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63214,0.14369,0.2334]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47613,-0.02007,-0.00203],"force_p95":0.1319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15172,"mean_force":0.12561,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4764,-0.01989,0.02536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11183.0,"contact_point_centroid":[0.55706,0.04541,0.23668],"force_p95":0.0801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13924,"mean_force":0.05501,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55699,0.06459,0.23451]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49544,-0.01329,0.21594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12391.0,"contact_point_centroid":[0.55494,0.08136,0.23592],"force_p95":0.0763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13169,"mean_force":0.05019,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55466,0.06233,0.23398]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48708,-0.024,0.08181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.47544,-0.00068,0.02616],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09852,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47527,-0.01987,0.02424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.47549,-0.03908,0.02611],"force_p95":0.06852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09198,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47527,-0.01987,0.02424]}],"total_contact_groups":12},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62948,0.14726,0.19299],"final_tcp_position":[0.62891,0.1472,0.21165],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.76462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49184,-0.02746,0.12949],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":740.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48371,-0.02011,0.03297],"tcp_start":[0.49184,-0.02746,0.12949],"tcp_to_object_dist_end":0.01027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.01987,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13077,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11523.0,"raw_peak_contact_force":0.15172,"tcp_end":[0.47524,-0.01987,0.02421],"tcp_start":[0.48371,-0.02011,0.03297],"tcp_to_object_dist_end":0.00181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.48717,-0.01961,0.21799],"object_pos_start":[0.47602,-0.01987,0.02585],"object_to_goal_dist_end":0.23144,"object_to_goal_dist_start":0.28839,"object_z_max":0.21771,"peak_contact_force":0.08183,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24058.0,"raw_peak_contact_force":0.76462,"subtask_id":"lift_object","tcp_end":[0.4729,-0.01978,0.21899],"tcp_start":[0.47524,-0.01987,0.02421],"tcp_to_object_dist_end":0.0143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.63731,0.14092,0.23383],"object_pos_start":[0.48717,-0.01961,0.21799],"object_to_goal_dist_end":0.04784,"object_to_goal_dist_start":0.23144,"object_z_max":0.23382,"peak_contact_force":0.0761,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23574.0,"raw_peak_contact_force":0.13924,"subtask_id":"place_goal","tcp_end":[0.63464,0.14066,0.25134],"tcp_start":[0.4729,-0.01978,0.21899],"tcp_to_object_dist_end":0.01771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.62948,0.14726,0.19299],"object_pos_start":[0.63731,0.14092,0.23383],"object_to_goal_dist_end":0.01245,"object_to_goal_dist_start":0.04784,"object_z_max":0.23383,"peak_contact_force":0.07571,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3000.0,"raw_peak_contact_force":0.16853,"subtask_id":"place_goal","tcp_end":[0.62891,0.1472,0.21165],"tcp_start":[0.63464,0.14066,0.25134],"tcp_to_object_dist_end":0.01866,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92558,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.04281,"approach_goal.approach_goal_y":0.0185,"approach_goal.approach_goal_z":0.08709,"approach_goal.approach_speed":0.07821,"approach_object.approach_offset_x":0.01923,"approach_object.approach_offset_y":0.01006,"approach_object.approach_offset_z":0.08324,"descend_to_grasp.descend_grasp_x":0.01055,"descend_to_grasp.descend_grasp_y":0.00105,"descend_to_grasp.descend_grasp_z":-0.01346,"descend_to_place.place_x":0.00314,"descend_to_place.place_y":-0.00345,"descend_to_place.place_z":0.007,"lift.lift_height":0.21037},"optimized_scores":{"best_composite_score":0.17867,"best_fitness_score":0.99867,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.4556,-0.02168,-0.00177],"force_p95":0.7244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79597,"mean_force":0.16821,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45757,-0.02267,0.02614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11712.0,"contact_point_centroid":[0.4554,-0.04182,0.12193],"force_p95":0.07889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33895,"mean_force":0.05088,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45524,-0.02265,0.12004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11628.0,"contact_point_centroid":[0.45539,-0.00349,0.12133],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30518,"mean_force":0.04995,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45524,-0.02265,0.11939]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45851,-0.02569,-0.00239],"force_p95":0.22275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30102,"mean_force":0.1521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46006,-0.02275,0.02512]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1689.0,"contact_point_centroid":[0.65164,0.23039,0.17006],"force_p95":0.08458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26934,"mean_force":0.06016,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.651,0.21132,0.16739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2034.0,"contact_point_centroid":[0.6512,0.19224,0.16944],"force_p95":0.07526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17688,"mean_force":0.05015,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.65104,0.21134,0.16749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4642.0,"contact_point_centroid":[0.45915,-0.00351,0.02604],"force_p95":0.0832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15225,"mean_force":0.04569,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45897,-0.02271,0.02408]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4886,-0.00676,0.21798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16367.0,"contact_point_centroid":[0.56011,0.07958,0.20387],"force_p95":0.08007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1351,"mean_force":0.05665,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55893,0.09862,0.20188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16604.0,"contact_point_centroid":[0.55789,0.11513,0.20392],"force_p95":0.08437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12724,"mean_force":0.05555,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55668,0.0961,0.20204]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47173,-0.01825,0.08319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5235.0,"contact_point_centroid":[0.45919,-0.04227,0.026],"force_p95":0.08415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08973,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45898,-0.02271,0.02409]}],"total_contact_groups":12},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.6418,0.20697,0.12444],"final_tcp_position":[0.64035,0.20732,0.13927],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.79597,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47764,-0.01401,0.13306],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46718,-0.02288,0.03225],"tcp_start":[0.47764,-0.01401,0.13306],"tcp_to_object_dist_end":0.01117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45837,-0.02285,0.02459],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30151,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.20151,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11677.0,"raw_peak_contact_force":0.30102,"tcp_end":[0.45894,-0.02271,0.02405],"tcp_start":[0.46718,-0.02288,0.03225],"tcp_to_object_dist_end":0.0008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.46829,-0.02271,0.21382],"object_pos_start":[0.45837,-0.02285,0.02459],"object_to_goal_dist_end":0.2991,"object_to_goal_dist_start":0.30151,"object_z_max":0.21353,"peak_contact_force":0.08356,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23429.0,"raw_peak_contact_force":0.79597,"subtask_id":"lift_object","tcp_end":[0.45539,-0.02271,0.21542],"tcp_start":[0.45894,-0.02271,0.02405],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.66843,0.21387,0.17966],"object_pos_start":[0.46829,-0.02271,0.21382],"object_to_goal_dist_end":0.07613,"object_to_goal_dist_start":0.2991,"object_z_max":0.21407,"peak_contact_force":0.08383,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32971.0,"raw_peak_contact_force":0.1351,"subtask_id":"place_goal","tcp_end":[0.66012,0.21412,0.19254],"tcp_start":[0.45539,-0.02271,0.21542],"tcp_to_object_dist_end":0.01533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.6418,0.20697,0.12444],"object_pos_start":[0.66843,0.21387,0.17966],"object_to_goal_dist_end":0.01563,"object_to_goal_dist_start":0.07613,"object_z_max":0.17966,"peak_contact_force":0.07606,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3723.0,"raw_peak_contact_force":0.26934,"subtask_id":"place_goal","tcp_end":[0.64035,0.20732,0.13927],"tcp_start":[0.66012,0.21412,0.19254],"tcp_to_object_dist_end":0.01491,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93243,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":-0.012,"approach_goal.approach_goal_y":0.01142,"approach_goal.approach_goal_z":0.04837,"approach_goal.approach_speed":0.17003,"approach_object.approach_offset_x":0.01287,"approach_object.approach_offset_y":-0.01693,"approach_object.approach_offset_z":0.0731,"descend_to_grasp.descend_grasp_x":0.0173,"descend_to_grasp.descend_grasp_y":0.0088,"descend_to_grasp.descend_grasp_z":-0.00634,"descend_to_place.place_x":0.001,"descend_to_place.place_y":-0.00412,"descend_to_place.place_z":-0.00074,"lift.lift_height":0.18231},"optimized_scores":{"best_composite_score":0.17865,"best_fitness_score":0.99865,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.5411,0.00513,-0.00172],"force_p95":0.65862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81754,"mean_force":0.15986,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54291,0.00416,0.02749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11020.0,"contact_point_centroid":[0.54063,-0.01512,0.10752],"force_p95":0.07778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35332,"mean_force":0.05092,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54024,0.00403,0.10561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11020.0,"contact_point_centroid":[0.54031,0.02319,0.10747],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31689,"mean_force":0.04998,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54024,0.00403,0.10561]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54426,0.00164,-0.00235],"force_p95":0.26782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30524,"mean_force":0.1806,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54572,0.00426,0.02696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4685.0,"contact_point_centroid":[0.54457,0.02341,0.02739],"force_p95":0.08432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20334,"mean_force":0.05242,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54447,0.00421,0.02548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.6299,0.17633,0.21948],"force_p95":0.08068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15845,"mean_force":0.053,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62981,0.15706,0.21768]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.63026,0.13805,0.21963],"force_p95":0.07519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13988,"mean_force":0.04994,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62981,0.15706,0.21768]},{"body_a":"world","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52221,-0.00676,0.21078]},{"body_a":"world","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54928,-0.0054,0.07856]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10096.0,"contact_point_centroid":[0.58279,0.10044,0.2074],"force_p95":0.07646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11242,"mean_force":0.04974,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58268,0.08138,0.20555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9339.0,"contact_point_centroid":[0.58468,0.06496,0.20859],"force_p95":0.07848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11166,"mean_force":0.05367,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58427,0.08413,0.20636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5183.0,"contact_point_centroid":[0.54479,-0.01525,0.02744],"force_p95":0.0824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09795,"mean_force":0.05021,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54448,0.00421,0.0255]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64193,0.15602,0.19066],"final_tcp_position":[0.63496,0.15569,0.20469],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.81754,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1460.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.54685,-0.01392,0.1198],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":652.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55378,0.00426,0.03673],"tcp_start":[0.54685,-0.01392,0.1198],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5441,0.00403,0.02473],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24925,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.26178,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11668.0,"raw_peak_contact_force":0.30524,"tcp_end":[0.54444,0.00421,0.02545],"tcp_start":[0.55378,0.00426,0.03673],"tcp_to_object_dist_end":0.00081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.55072,0.00397,0.18478],"object_pos_start":[0.5441,0.00403,0.02473],"object_to_goal_dist_end":0.18216,"object_to_goal_dist_start":0.24925,"object_z_max":0.18452,"peak_contact_force":0.07551,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22139.0,"raw_peak_contact_force":0.81754,"subtask_id":"lift_object","tcp_end":[0.54053,0.00396,0.18753],"tcp_start":[0.54444,0.00421,0.02545],"tcp_to_object_dist_end":0.01056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.63038,0.1572,0.21336],"object_pos_start":[0.55072,0.00397,0.18478],"object_to_goal_dist_end":0.02817,"object_to_goal_dist_start":0.18216,"object_z_max":0.21332,"peak_contact_force":0.07707,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19435.0,"raw_peak_contact_force":0.11242,"subtask_id":"place_goal","tcp_end":[0.6262,0.15707,0.22735],"tcp_start":[0.54053,0.00396,0.18753],"tcp_to_object_dist_end":0.0146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.64193,0.15602,0.19066],"object_pos_start":[0.63038,0.1572,0.21336],"object_to_goal_dist_end":0.00607,"object_to_goal_dist_start":0.02817,"object_z_max":0.21336,"peak_contact_force":0.07614,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2160.0,"raw_peak_contact_force":0.15845,"subtask_id":"place_goal","tcp_end":[0.63496,0.15569,0.20469],"tcp_start":[0.6262,0.15707,0.22735],"tcp_to_object_dist_end":0.01567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```