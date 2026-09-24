## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1781 | 1.00 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1146 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1159 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15  | 0.1076 | 0.90 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14  | 0.1779 | 1.00 | ❌ rejected |

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
| approach_object | 1.00 | 1.00 | 0.1680 |
| descend_to_grasp | 1.00 | 1.00 | 0.1067 |
| grasp | 1.00 | 1.00 | 0.0128 |
| lift | 1.00 | 1.00 | 0.1773 |
| approach_goal | 1.00 | 1.00 | 0.2594 |
| descend_to_place | 1.00 | 1.00 | 0.0360 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, -0.010, 0.138) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, -0.010, 0.138)→(0.502, -0.012, 0.033) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.502, -0.012, 0.033)→(0.493, -0.012, 0.023) | (0.493, -0.015, 0.026)→(0.493, -0.012, 0.024) | 0.281→0.280 | 1.00 / 44.000 | 0.226 | 0.332 |
| lift | lift | 1.00 / step_budget | (0.493, -0.012, 0.023)→(0.490, -0.012, 0.200) | (0.493, -0.012, 0.024)→(0.501, -0.012, 0.199) | 0.280→0.236 | 1.00 / 43.000 | 55983.959 | 0.835 |
| approach_goal | approach | 1.00 / step_budget | (0.490, -0.012, 0.200)→(0.650, 0.182, 0.217) | (0.501, -0.012, 0.199)→(0.651, 0.182, 0.202) | 0.236→0.042 | 1.00 / 41.333 | 0.073 | 0.122 |
| descend_to_place | descend | 1.00 / step_budget | (0.650, 0.182, 0.217)→(0.642, 0.181, 0.182) | (0.651, 0.182, 0.202)→(0.642, 0.181, 0.166) | 0.042→0.011 | 1.00 / 40.000 | 0.074 | 0.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.484
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.542
- phase_breakdown.lift_object_score: 0.574
- phase_breakdown.reach_object_score: 0.143
- phase_breakdown.place_goal_score: 0.682
- grasp_place_fitness: 0.999

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.999
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.178
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91803,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.03438,"approach_goal.approach_goal_y":0.00913,"approach_goal.approach_goal_z":0.08788,"approach_goal.approach_speed":0.0986,"approach_object.approach_offset_x":-0.00331,"approach_object.approach_offset_y":0.0041,"approach_object.approach_offset_z":0.10574,"descend_to_grasp.descend_grasp_x":0.01546,"descend_to_grasp.descend_grasp_y":0.00258,"descend_to_grasp.descend_grasp_z":-0.0119,"descend_to_place.place_x":0.0094,"descend_to_place.place_y":0.00291,"descend_to_place.place_z":-0.00465,"lift.lift_height":0.1863},"optimized_scores":{"best_composite_score":0.17849,"best_fitness_score":0.99849,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.47323,-0.01567,-0.00174],"force_p95":0.73421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80901,"mean_force":0.16552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47501,-0.01672,0.02595]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10346.0,"contact_point_centroid":[0.47283,-0.03588,0.10869],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34001,"mean_force":0.05115,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47261,-0.01671,0.10679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10350.0,"contact_point_centroid":[0.47281,0.00244,0.1087],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31002,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47261,-0.01671,0.10683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47611,-0.01955,-0.00238],"force_p95":0.21857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29795,"mean_force":0.15097,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47758,-0.01676,0.02502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.64928,0.17846,0.23952],"force_p95":0.07817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16279,"mean_force":0.05233,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64928,0.15937,0.23746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.64921,0.14016,0.23939],"force_p95":0.0794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16158,"mean_force":0.05235,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64923,0.15938,0.23721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4653.0,"contact_point_centroid":[0.47663,0.00246,0.02584],"force_p95":0.08223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15571,"mean_force":0.04559,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47645,-0.01674,0.02389]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.47616,-0.02015,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.487,-0.0065,0.22937]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47837,-0.01515,0.09438]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15775.0,"contact_point_centroid":[0.56634,0.05541,0.22985],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11715,"mean_force":0.05371,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56575,0.0745,0.22765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15305.0,"contact_point_centroid":[0.56374,0.09102,0.22877],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11528,"mean_force":0.05467,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56302,0.07193,0.22647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5219.0,"contact_point_centroid":[0.47667,-0.03627,0.02583],"force_p95":0.08318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08851,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47647,-0.01674,0.02391]}],"total_contact_groups":12},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.64127,0.15978,0.18713],"final_tcp_position":[0.6431,0.16015,0.20465],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.80901,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47405,-0.01356,0.1555],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":976.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48481,-0.01684,0.03259],"tcp_start":[0.47405,-0.01356,0.1555],"tcp_to_object_dist_end":0.01136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47597,-0.01686,0.02464],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28724,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.19847,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11672.0,"raw_peak_contact_force":0.29795,"tcp_end":[0.47643,-0.01674,0.02387],"tcp_start":[0.48481,-0.01684,0.03259],"tcp_to_object_dist_end":0.00091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.48373,-0.01684,0.19032],"object_pos_start":[0.47597,-0.01686,0.02464],"object_to_goal_dist_end":0.22979,"object_to_goal_dist_start":0.28724,"object_z_max":0.19003,"peak_contact_force":0.07363,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20787.0,"raw_peak_contact_force":0.80901,"subtask_id":"lift_object","tcp_end":[0.47272,-0.01676,0.19124],"tcp_start":[0.47643,-0.01674,0.02387],"tcp_to_object_dist_end":0.01105,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.65791,0.15849,0.24901],"object_pos_start":[0.48373,-0.01684,0.19032],"object_to_goal_dist_end":0.06467,"object_to_goal_dist_start":0.22979,"object_z_max":0.24898,"peak_contact_force":0.06659,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31080.0,"raw_peak_contact_force":0.11715,"subtask_id":"place_goal","tcp_end":[0.65424,0.15847,0.26489],"tcp_start":[0.47272,-0.01676,0.19124],"tcp_to_object_dist_end":0.0163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.64127,0.15978,0.18713],"object_pos_start":[0.65791,0.15849,0.24901],"object_to_goal_dist_end":0.01028,"object_to_goal_dist_start":0.06467,"object_z_max":0.24901,"peak_contact_force":0.07104,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4260.0,"raw_peak_contact_force":0.16279,"subtask_id":"place_goal","tcp_end":[0.6431,0.16015,0.20465],"tcp_start":[0.65424,0.15847,0.26489],"tcp_to_object_dist_end":0.01762,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81421,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.03266,"approach_goal.approach_goal_y":0.0238,"approach_goal.approach_goal_z":0.03873,"approach_goal.approach_speed":0.12548,"approach_object.approach_offset_x":0.03368,"approach_object.approach_offset_y":-0.00832,"approach_object.approach_offset_z":0.06386,"descend_to_grasp.descend_grasp_x":0.00588,"descend_to_grasp.descend_grasp_y":-0.00302,"descend_to_grasp.descend_grasp_z":-0.01226,"descend_to_place.place_x":0.00199,"descend_to_place.place_y":-0.00204,"descend_to_place.place_z":-0.00123,"lift.lift_height":0.20207},"optimized_scores":{"best_composite_score":0.17916,"best_fitness_score":0.99916,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.45556,-0.03014,-0.00169],"force_p95":0.70724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76573,"mean_force":0.16726,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45746,-0.02902,0.02708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11168.0,"contact_point_centroid":[0.45529,-0.0097,0.11859],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33578,"mean_force":0.05063,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45516,-0.02883,0.11663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11133.0,"contact_point_centroid":[0.45531,-0.04801,0.11819],"force_p95":0.07553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30555,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45516,-0.02883,0.11636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45852,-0.02677,-0.00231],"force_p95":0.20088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28086,"mean_force":0.14557,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4599,-0.02912,0.02624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64636,0.2364,0.14077],"force_p95":0.09164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2141,"mean_force":0.05529,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64614,0.21722,0.13893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64643,0.19811,0.14086],"force_p95":0.07522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17187,"mean_force":0.04873,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64614,0.21722,0.13893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4700.0,"contact_point_centroid":[0.45902,-0.04827,0.02706],"force_p95":0.07863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16461,"mean_force":0.04522,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45882,-0.02907,0.02519]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49441,-0.01469,0.20789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17173.0,"contact_point_centroid":[0.55429,0.11716,0.1763],"force_p95":0.07618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12283,"mean_force":0.05025,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55389,0.09819,0.17441]},{"body_a":"world","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47824,-0.02994,0.07388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14988.0,"contact_point_centroid":[0.55557,0.08052,0.17645],"force_p95":0.08203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11866,"mean_force":0.05653,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55515,0.09974,0.17407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5146.0,"contact_point_centroid":[0.45902,-0.00966,0.02719],"force_p95":0.07964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08794,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45883,-0.02907,0.02521]}],"total_contact_groups":12},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63805,0.21427,0.11147],"final_tcp_position":[0.6411,0.21391,0.12876],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.76573,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48983,-0.03034,0.11313],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":616.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46704,-0.02942,0.03334],"tcp_start":[0.48983,-0.03034,0.11313],"tcp_to_object_dist_end":0.01162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45839,-0.02893,0.02489],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30609,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.18527,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11646.0,"raw_peak_contact_force":0.28086,"tcp_end":[0.45879,-0.02907,0.02517],"tcp_start":[0.46704,-0.02942,0.03334],"tcp_to_object_dist_end":0.00051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.4677,-0.02877,0.20523],"object_pos_start":[0.45839,-0.02893,0.02489],"object_to_goal_dist_end":0.30141,"object_to_goal_dist_start":0.30609,"object_z_max":0.20495,"peak_contact_force":0.07177,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22386.0,"raw_peak_contact_force":0.76573,"subtask_id":"lift_object","tcp_end":[0.45534,-0.02877,0.20743],"tcp_start":[0.45879,-0.02907,0.02517],"tcp_to_object_dist_end":0.01255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.64751,0.21856,0.13008],"object_pos_start":[0.4677,-0.02877,0.20523],"object_to_goal_dist_end":0.02576,"object_to_goal_dist_start":0.30141,"object_z_max":0.2055,"peak_contact_force":0.07441,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32161.0,"raw_peak_contact_force":0.12283,"subtask_id":"place_goal","tcp_end":[0.64973,0.21858,0.14624],"tcp_start":[0.45534,-0.02877,0.20743],"tcp_to_object_dist_end":0.01631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.63805,0.21427,0.11147],"object_pos_start":[0.64751,0.21856,0.13008],"object_to_goal_dist_end":0.01031,"object_to_goal_dist_start":0.02576,"object_z_max":0.13008,"peak_contact_force":0.07579,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1600.0,"raw_peak_contact_force":0.2141,"subtask_id":"place_goal","tcp_end":[0.6411,0.21391,0.12876],"tcp_start":[0.64973,0.21858,0.14624],"tcp_to_object_dist_end":0.01756,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78882,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_x":0.00812,"approach_goal.approach_goal_y":0.0236,"approach_goal.approach_goal_z":0.06074,"approach_goal.approach_speed":0.13321,"approach_object.approach_offset_x":0.02202,"approach_object.approach_offset_y":0.01607,"approach_object.approach_offset_z":0.10014,"descend_to_grasp.descend_grasp_x":0.01437,"descend_to_grasp.descend_grasp_y":0.00825,"descend_to_grasp.descend_grasp_z":-0.01324,"descend_to_place.place_x":-0.00535,"descend_to_place.place_y":0.01048,"descend_to_place.place_z":0.00246,"lift.lift_height":0.19917},"optimized_scores":{"best_composite_score":0.17612,"best_fitness_score":0.99612,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.54103,0.01137,-0.0023],"force_p95":0.69661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93092,"mean_force":0.16275,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54213,0.0098,0.02361]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54421,0.00302,-0.00288],"force_p95":0.34477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41617,"mean_force":0.1923,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54521,0.00991,0.02201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12417.0,"contact_point_centroid":[0.5401,-0.00949,0.11308],"force_p95":0.08694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38855,"mean_force":0.05203,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53989,0.00969,0.11112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12415.0,"contact_point_centroid":[0.54006,0.02892,0.11306],"force_p95":0.08658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33629,"mean_force":0.0494,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53989,0.00969,0.11127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.64451,0.18892,0.2303],"force_p95":0.07813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15973,"mean_force":0.05199,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64427,0.16968,0.22854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.64458,0.15063,0.23055],"force_p95":0.07467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15,"mean_force":0.04915,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64427,0.16968,0.22854]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52588,0.0072,0.2235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3835.0,"contact_point_centroid":[0.54399,0.02927,0.02356],"force_p95":0.10305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13025,"mean_force":0.05508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54394,0.00986,0.02053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10537.0,"contact_point_centroid":[0.59576,0.07526,0.22253],"force_p95":0.08332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12594,"mean_force":0.05561,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59506,0.09441,0.22012]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.55295,0.01268,0.08931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5517.0,"contact_point_centroid":[0.54427,-0.01095,0.02218],"force_p95":0.10496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11873,"mean_force":0.04966,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.544,0.00986,0.0206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11421.0,"contact_point_centroid":[0.59458,0.11207,0.22151],"force_p95":0.07876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11088,"mean_force":0.05108,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59406,0.09303,0.21966]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64655,0.16897,0.19822],"final_tcp_position":[0.64248,0.16894,0.21334],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.55437,0.01485,0.14553],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.55334,0.01027,0.0319],"tcp_start":[0.55437,0.01485,0.14553],"tcp_to_object_dist_end":0.01413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54391,0.00978,0.02286],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2471,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.29448,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11152.0,"raw_peak_contact_force":0.41617,"tcp_end":[0.54392,0.00988,0.02051],"tcp_start":[0.55334,0.01027,0.0319],"tcp_to_object_dist_end":0.00235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.5524,0.00961,0.20233],"object_pos_start":[0.54391,0.00978,0.02286],"object_to_goal_dist_end":0.17674,"object_to_goal_dist_start":0.2471,"object_z_max":0.20208,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24953.0,"raw_peak_contact_force":0.93092,"subtask_id":"lift_object","tcp_end":[0.54047,0.00967,0.20252],"tcp_start":[0.54392,0.00988,0.02051],"tcp_to_object_dist_end":0.01194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.64864,0.16932,0.22553],"object_pos_start":[0.5524,0.00961,0.20233],"object_to_goal_dist_end":0.03623,"object_to_goal_dist_start":0.17674,"object_z_max":0.22551,"peak_contact_force":0.07681,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21958.0,"raw_peak_contact_force":0.12594,"subtask_id":"place_goal","tcp_end":[0.64564,0.16948,0.2397],"tcp_start":[0.54047,0.00967,0.20252],"tcp_to_object_dist_end":0.01448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.64655,0.16897,0.19822],"object_pos_start":[0.64864,0.16932,0.22553],"object_to_goal_dist_end":0.01305,"object_to_goal_dist_start":0.03623,"object_z_max":0.22553,"peak_contact_force":0.07558,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.15973,"subtask_id":"place_goal","tcp_end":[0.64248,0.16894,0.21334],"tcp_start":[0.64564,0.16948,0.2397],"tcp_to_object_dist_end":0.01565,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```