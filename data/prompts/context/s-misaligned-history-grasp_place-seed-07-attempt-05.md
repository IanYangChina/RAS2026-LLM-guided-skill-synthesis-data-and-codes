## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.1669 | 0.75 | ✅ accepted |
| 4 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2528 | 0.33 | ✅ accepted |
| 3 | descend → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | -0.2841 | 0.17 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.2211 | 0.19 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.2932 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=0.293) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_grasp_height
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_above
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_goal
  weight: 0.3
phases:
- id: descend_approach
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp_height
- id: grasp_object
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
    tolerance: 0.005
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: reach_grasp_height
- id: lift_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_above
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_height_offset:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_approach** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.293
- **task_score** (E): 1.000
- **fitness_score**: 0.963  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1348 |
| descend_to_grasp | 1.00 | 1.00 | 0.1170 |
| grasp_object | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1185 |
| transport_to_goal | 1.00 | 1.00 | 0.2266 |
| descend_to_place | 1.00 | 1.00 | 0.0466 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.018, 0.171) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.018, 0.171)→(0.506, 0.022, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 9.167 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.055)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.667 | 0.153 | 0.210 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.046)→(0.506, 0.021, 0.164) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.141) | 0.274→0.221 | 1.00 / 37.667 | 0.082 | 0.351 |
| transport_to_goal | approach | 1.00 / step_budget | (0.506, 0.021, 0.164)→(0.594, 0.189, 0.282) | (0.514, 0.022, 0.141)→(0.601, 0.189, 0.253) | 0.221→0.063 | 1.00 / 25.333 | 0.107 | 0.153 |
| descend_to_place | descend | 1.00 / step_budget | (0.594, 0.189, 0.282)→(0.600, 0.202, 0.238) | (0.601, 0.189, 0.253)→(0.608, 0.202, 0.208) | 0.063→0.016 | 1.00 / 22.667 | 0.125 | 0.442 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.125
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.567
- phase_breakdown.reach_grasp_height_score: 0.655
- phase_breakdown.lift_clearance_score: 0.788
- phase_breakdown.reach_goal_score: 0.402
- phase_breakdown.transport_above_score: 0.494
- phase_breakdown.reach_approach_score: 0.540
- grasp_place_fitness: 0.964

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.964
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.293
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.65508,"average_solve_count":374.0,"average_success_count":374.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.142,"descend_approach.approach_speed":0.05907,"descend_to_grasp.descend_speed":0.04162,"descend_to_grasp.grasp_height":0.02031,"descend_to_place.place_height_offset":0.03399,"descend_to_place.place_speed":0.02052,"lift_object.lift_height":0.14514,"lift_object.lift_speed":0.02167,"transport_to_goal.arc_height":0.15847,"transport_to_goal.transport_height":0.07711,"transport_to_goal.transport_speed":0.04432},"optimized_scores":{"best_composite_score":0.29308,"best_fitness_score":0.96308,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1346.0,"contact_point_centroid":[0.61883,0.18093,0.20728],"force_p95":0.10302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38255,"mean_force":0.07281,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61524,0.16208,0.20822]},{"body_a":"world","body_b":"grasp_target","contact_count":122.0,"contact_point_centroid":[0.50966,0.03788,-0.00166],"force_p95":0.29656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3399,"mean_force":0.13921,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49832,0.03789,0.04643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1271.0,"contact_point_centroid":[0.61826,0.1434,0.20738],"force_p95":0.10176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29275,"mean_force":0.07307,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6152,0.16204,0.20846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8947.0,"contact_point_centroid":[0.5013,0.057,0.09675],"force_p95":0.07723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23217,"mean_force":0.0498,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50137,0.0379,0.09481]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0396,-0.00215],"force_p95":0.1632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22209,"mean_force":0.13332,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50059,0.03809,0.04688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7747.0,"contact_point_centroid":[0.50098,0.0187,0.0979],"force_p95":0.08171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20917,"mean_force":0.05528,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50152,0.03791,0.09614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12769.0,"contact_point_centroid":[0.54595,0.10151,0.21445],"force_p95":0.08217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1422,"mean_force":0.05458,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54463,0.08245,0.21334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4331.0,"contact_point_centroid":[0.49973,0.01876,0.04744],"force_p95":0.07786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13936,"mean_force":0.04961,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49944,0.038,0.0456]},{"body_a":"world","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.51251,0.03972,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50289,0.0153,0.24631]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12875.0,"contact_point_centroid":[0.5455,0.06375,0.21417],"force_p95":0.08211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13496,"mean_force":0.054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54494,0.0828,0.21349]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50595,0.03535,0.12114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5261.0,"contact_point_centroid":[0.50007,0.05717,0.0477],"force_p95":0.07172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0738,"mean_force":0.04224,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49944,0.038,0.0456]}],"total_contact_groups":12},"final_pose_error":0.0147,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62686,0.1665,0.16117],"final_tcp_position":[0.61912,0.16634,0.18934],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":27.25618,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":940.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50731,0.03229,0.18959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":27.25618,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50745,0.03863,0.05462],"tcp_start":[0.50731,0.03229,0.18959],"tcp_to_object_dist_end":0.02906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.0385,0.02548],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21331,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15962,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11392.0,"raw_peak_contact_force":0.22209,"subtask_id":"reach_grasp_height","tcp_end":[0.49941,0.038,0.04557],"tcp_start":[0.50745,0.03863,0.05462],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.51616,0.0386,0.12862],"object_pos_start":[0.51248,0.0385,0.02548],"object_to_goal_dist_end":0.17498,"object_to_goal_dist_start":0.21331,"object_z_max":0.12837,"peak_contact_force":0.08173,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16816.0,"raw_peak_contact_force":0.3399,"subtask_id":"lift_clearance","tcp_end":[0.5073,0.03813,0.15139],"tcp_start":[0.49941,0.038,0.04557],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.61977,0.15895,0.19722],"object_pos_start":[0.51616,0.0386,0.12862],"object_to_goal_dist_end":0.05449,"object_to_goal_dist_start":0.17498,"object_z_max":0.21467,"peak_contact_force":0.09054,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25644.0,"raw_peak_contact_force":0.1422,"subtask_id":"transport_above","tcp_end":[0.61338,0.1588,0.2247],"tcp_start":[0.5073,0.03813,0.15139],"tcp_to_object_dist_end":0.02821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.62686,0.1665,0.16117],"object_pos_start":[0.61977,0.15895,0.19722],"object_to_goal_dist_end":0.01724,"object_to_goal_dist_start":0.05449,"object_z_max":0.19722,"peak_contact_force":0.10132,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2617.0,"raw_peak_contact_force":0.38255,"subtask_id":"reach_goal","tcp_end":[0.61912,0.16634,0.18934],"tcp_start":[0.61338,0.1588,0.2247],"tcp_to_object_dist_end":0.02921,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72746,"average_solve_count":488.0,"average_success_count":488.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.11731,"descend_approach.approach_speed":0.03014,"descend_to_grasp.descend_speed":0.03115,"descend_to_grasp.grasp_height":0.02002,"descend_to_place.place_height_offset":0.03137,"descend_to_place.place_speed":0.0199,"lift_object.lift_height":0.16448,"lift_object.lift_speed":0.02374,"transport_to_goal.arc_height":0.1008,"transport_to_goal.transport_height":0.08298,"transport_to_goal.transport_speed":0.03575},"optimized_scores":{"best_composite_score":0.29243,"best_fitness_score":0.96243,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.57892,0.23497,0.29616],"force_p95":0.10877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47315,"mean_force":0.07862,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57308,0.21686,0.29706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":933.0,"contact_point_centroid":[0.57815,0.19831,0.29404],"force_p95":0.13999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4004,"mean_force":0.11332,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57305,0.21682,0.29724]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.47962,0.04664,-0.00167],"force_p95":0.31081,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34777,"mean_force":0.14738,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46957,0.04657,0.04755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9225.0,"contact_point_centroid":[0.47277,0.06562,0.10727],"force_p95":0.08089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24474,"mean_force":0.05244,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47248,0.04662,0.10577]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.0486,-0.00216],"force_p95":0.16774,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22767,"mean_force":0.13457,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4717,0.0468,0.04779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7682.0,"contact_point_centroid":[0.47185,0.02743,0.10801],"force_p95":0.0891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21188,"mean_force":0.06015,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47256,0.04662,0.1067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16509.0,"contact_point_centroid":[0.49955,0.10306,0.27673],"force_p95":0.09613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16794,"mean_force":0.06061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49738,0.08427,0.27655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15652.0,"contact_point_centroid":[0.49702,0.06274,0.2764],"force_p95":0.12014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16028,"mean_force":0.06441,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49587,0.08167,0.27665]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49079,0.0194,0.23471]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47884,0.04407,0.10945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4683.0,"contact_point_centroid":[0.46989,0.02746,0.04838],"force_p95":0.07231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11477,"mean_force":0.04607,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47061,0.04669,0.04665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5286.0,"contact_point_centroid":[0.47048,0.06596,0.04823],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07465,"mean_force":0.04242,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47061,0.04669,0.04666]}],"total_contact_groups":12},"final_pose_error":0.01469,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58372,0.22333,0.24117],"final_tcp_position":[0.57626,0.22231,0.27375],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.47315,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48217,0.04103,0.16527],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47829,0.04742,0.05471],"tcp_start":[0.48217,0.04103,0.16527],"tcp_to_object_dist_end":0.02906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04732,0.02541],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29129,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16405,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11769.0,"raw_peak_contact_force":0.22767,"subtask_id":"reach_grasp_height","tcp_end":[0.47058,0.04669,0.04662],"tcp_start":[0.47829,0.04742,0.05471],"tcp_to_object_dist_end":0.02443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.48536,0.04725,0.14668],"object_pos_start":[0.48268,0.04732,0.02541],"object_to_goal_dist_end":0.22208,"object_to_goal_dist_start":0.29129,"object_z_max":0.14641,"peak_contact_force":0.08817,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17017.0,"raw_peak_contact_force":0.34777,"subtask_id":"lift_clearance","tcp_end":[0.47803,0.04691,0.17071],"tcp_start":[0.47058,0.04669,0.04662],"tcp_to_object_dist_end":0.02513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.57806,0.21326,0.28629],"object_pos_start":[0.48536,0.04725,0.14668],"object_to_goal_dist_end":0.05807,"object_to_goal_dist_start":0.22208,"object_z_max":0.31052,"peak_contact_force":0.13371,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32161.0,"raw_peak_contact_force":0.16794,"subtask_id":"transport_above","tcp_end":[0.57151,0.21259,0.31785],"tcp_start":[0.47803,0.04691,0.17071],"tcp_to_object_dist_end":0.03223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.58372,0.22333,0.24117],"object_pos_start":[0.57806,0.21326,0.28629],"object_to_goal_dist_end":0.01217,"object_to_goal_dist_start":0.05807,"object_z_max":0.28629,"peak_contact_force":0.13414,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2317.0,"raw_peak_contact_force":0.47315,"subtask_id":"reach_goal","tcp_end":[0.57626,0.22231,0.27375],"tcp_start":[0.57151,0.21259,0.31785],"tcp_to_object_dist_end":0.03343,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63928,"average_solve_count":499.0,"average_success_count":499.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.11181,"descend_approach.approach_speed":0.0292,"descend_to_grasp.descend_speed":0.02826,"descend_to_grasp.grasp_height":0.0202,"descend_to_place.place_height_offset":0.03487,"descend_to_place.place_speed":0.0175,"lift_object.lift_height":0.16277,"lift_object.lift_speed":0.02786,"transport_to_goal.arc_height":0.09375,"transport_to_goal.transport_height":0.08363,"transport_to_goal.transport_speed":0.03415},"optimized_scores":{"best_composite_score":0.294,"best_fitness_score":0.964,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.60707,0.22331,0.27942],"force_p95":0.13365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47053,"mean_force":0.08795,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60051,0.20454,0.27893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1883.0,"contact_point_centroid":[0.60657,0.18625,0.27858],"force_p95":0.09737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42055,"mean_force":0.07494,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60054,0.20465,0.27862]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.53391,-0.0208,-0.00153],"force_p95":0.32386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36422,"mean_force":0.14596,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52179,-0.02065,0.04515]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10294.0,"contact_point_centroid":[0.52536,-0.03982,0.10573],"force_p95":0.07539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22653,"mean_force":0.05111,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52528,-0.02068,0.10302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9838.0,"contact_point_centroid":[0.52533,-0.00151,0.10652],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22362,"mean_force":0.05284,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52534,-0.02068,0.10359]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02124,-0.00206],"force_p95":0.13833,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1815,"mean_force":0.1273,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52408,-0.02069,0.04579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16534.0,"contact_point_centroid":[0.55308,0.02671,0.2663],"force_p95":0.09124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14894,"mean_force":0.05982,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55052,0.04547,0.26585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14352.0,"contact_point_centroid":[0.55374,0.06492,0.26537],"force_p95":0.10626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14425,"mean_force":0.06844,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55069,0.046,0.26496]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51258,-0.00856,0.23172]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52813,-0.0194,0.10589]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5076.0,"contact_point_centroid":[0.52345,-0.0015,0.04748],"force_p95":0.06602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09777,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52288,-0.02067,0.04439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4907.0,"contact_point_centroid":[0.52377,-0.03994,0.04618],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08544,"mean_force":0.04505,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52288,-0.02067,0.04439]}],"total_contact_groups":12},"final_pose_error":0.01495,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61222,0.21705,0.22113],"final_tcp_position":[0.60455,0.21735,0.25134],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.47053,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52816,-0.01808,0.15929],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53121,-0.02082,0.05423],"tcp_start":[0.52816,-0.01808,0.15929],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02087,0.02577],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31653,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13612,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11783.0,"raw_peak_contact_force":0.1815,"subtask_id":"reach_grasp_height","tcp_end":[0.52285,-0.02067,0.04435],"tcp_start":[0.53121,-0.02082,0.05423],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.54107,-0.02082,0.1472],"object_pos_start":[0.53695,-0.02087,0.02577],"object_to_goal_dist_end":0.26497,"object_to_goal_dist_start":0.31653,"object_z_max":0.14695,"peak_contact_force":0.0765,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20241.0,"raw_peak_contact_force":0.36422,"subtask_id":"lift_clearance","tcp_end":[0.53195,-0.02077,0.16924],"tcp_start":[0.52285,-0.02067,0.04435],"tcp_to_object_dist_end":0.02386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60589,0.19423,0.2748],"object_pos_start":[0.54107,-0.02082,0.1472],"object_to_goal_dist_end":0.0754,"object_to_goal_dist_start":0.26497,"object_z_max":0.29356,"peak_contact_force":0.09752,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30886.0,"raw_peak_contact_force":0.14894,"subtask_id":"transport_above","tcp_end":[0.59843,0.19473,0.30403],"tcp_start":[0.53195,-0.02077,0.16924],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.61222,0.21705,0.22113],"object_pos_start":[0.60589,0.19423,0.2748],"object_to_goal_dist_end":0.0175,"object_to_goal_dist_start":0.0754,"object_z_max":0.2748,"peak_contact_force":0.14078,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3539.0,"raw_peak_contact_force":0.47053,"subtask_id":"reach_goal","tcp_end":[0.60455,0.21735,0.25134],"tcp_start":[0.59843,0.19473,0.30403],"tcp_to_object_dist_end":0.03117,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```