## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2932 | 1.00 | ✅ accepted |
| 5 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.1669 | 0.75 | ✅ accepted |
| 4 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2528 | 0.33 | ✅ accepted |
| 3 | descend → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | -0.2841 | 0.17 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | 0.2924 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.292) — your mutation base

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

- **Composite score**: 0.292
- **task_score** (E): 1.000
- **fitness_score**: 0.962  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1433 |
| descend_to_grasp | 1.00 | 1.00 | 0.1078 |
| grasp_object | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1251 |
| transport_to_goal | 1.00 | 1.00 | 0.2442 |
| descend_to_place | 1.00 | 1.00 | 0.0760 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.018, 0.163) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 7.768 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.018, 0.163)→(0.506, 0.022, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 7.784 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.055)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 42.667 | 0.154 | 0.211 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.046)→(0.506, 0.021, 0.171) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.147) | 0.274→0.223 | 1.00 / 37.667 | 0.082 | 0.378 |
| transport_to_goal | approach | 1.00 / step_budget | (0.506, 0.021, 0.171)→(0.595, 0.191, 0.313) | (0.514, 0.022, 0.147)→(0.600, 0.191, 0.284) | 0.223→0.092 | 1.00 / 25.667 | 0.112 | 0.158 |
| descend_to_place | descend | 1.00 / step_budget | (0.595, 0.191, 0.313)→(0.601, 0.204, 0.239) | (0.600, 0.191, 0.284)→(0.607, 0.204, 0.207) | 0.092→0.014 | 1.00 / 20.667 | 0.131 | 0.361 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.342
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.596
- phase_breakdown.reach_grasp_height_score: 0.670
- phase_breakdown.lift_clearance_score: 0.752
- phase_breakdown.reach_goal_score: 0.427
- phase_breakdown.transport_above_score: 0.459
- phase_breakdown.reach_approach_score: 0.686
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.292
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.grasp_height
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85849,"average_solve_count":424.0,"average_success_count":424.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.09919,"descend_approach.approach_speed":0.065,"descend_to_grasp.descend_speed":0.0303,"descend_to_grasp.grasp_height":0.02,"descend_to_place.place_height_offset":0.02888,"descend_to_place.place_speed":0.02151,"lift_object.lift_height":0.16045,"lift_object.lift_speed":0.03312,"transport_to_goal.arc_height":0.1356,"transport_to_goal.transport_height":0.13,"transport_to_goal.transport_speed":0.03815},"optimized_scores":{"best_composite_score":0.29333,"best_fitness_score":0.96333,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":101.0,"contact_point_centroid":[0.50937,0.03776,-0.00159],"force_p95":0.3523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38211,"mean_force":0.14346,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49821,0.03784,0.04621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.62032,0.18186,0.23359],"force_p95":0.10156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3513,"mean_force":0.07035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61656,0.16314,0.23468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2837.0,"contact_point_centroid":[0.61976,0.14453,0.23347],"force_p95":0.10511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33222,"mean_force":0.07283,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61657,0.16315,0.23472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9691.0,"contact_point_centroid":[0.50137,0.05694,0.1043],"force_p95":0.07841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25471,"mean_force":0.05043,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50139,0.03785,0.10218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8373.0,"contact_point_centroid":[0.50119,0.01865,0.10664],"force_p95":0.0819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23029,"mean_force":0.05605,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50162,0.03786,0.10458]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03958,-0.00215],"force_p95":0.1639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.224,"mean_force":0.1335,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50037,0.03802,0.04651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15975.0,"contact_point_centroid":[0.53591,0.09025,0.25411],"force_p95":0.0803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16048,"mean_force":0.05277,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53506,0.07118,0.25313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15682.0,"contact_point_centroid":[0.53661,0.05387,0.25629],"force_p95":0.08077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14598,"mean_force":0.05321,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53666,0.07295,0.25546]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50287,0.01631,0.225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.49961,0.0187,0.04719],"force_p95":0.07814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1371,"mean_force":0.04956,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49922,0.03793,0.04523]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50589,0.03613,0.10011]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5274.0,"contact_point_centroid":[0.49976,0.05712,0.0474],"force_p95":0.07181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07417,"mean_force":0.04222,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49923,0.03793,0.04524]}],"total_contact_groups":12},"final_pose_error":0.01493,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62813,0.16865,0.1576],"final_tcp_position":[0.62141,0.16861,0.18693],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.38211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50742,0.03396,0.1472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50727,0.03857,0.05425],"tcp_start":[0.50742,0.03396,0.1472],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03844,0.02547],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21334,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1601,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11404.0,"raw_peak_contact_force":0.224,"subtask_id":"reach_grasp_height","tcp_end":[0.49919,0.03793,0.0452],"tcp_start":[0.50727,0.03857,0.05425],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.51629,0.03853,0.14395],"object_pos_start":[0.51248,0.03844,0.02547],"object_to_goal_dist_end":0.17418,"object_to_goal_dist_start":0.21334,"object_z_max":0.14369,"peak_contact_force":0.0809,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18165.0,"raw_peak_contact_force":0.38211,"subtask_id":"lift_clearance","tcp_end":[0.50759,0.03809,0.1667],"tcp_start":[0.49919,0.03793,0.0452],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.61962,0.15886,0.25119],"object_pos_start":[0.51629,0.03853,0.14395],"object_to_goal_dist_end":0.10733,"object_to_goal_dist_start":0.17418,"object_z_max":0.2713,"peak_contact_force":0.0916,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31657.0,"raw_peak_contact_force":0.16048,"subtask_id":"transport_above","tcp_end":[0.61398,0.15882,0.2788],"tcp_start":[0.50759,0.03809,0.1667],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.62813,0.16865,0.1576],"object_pos_start":[0.61962,0.15886,0.25119],"object_to_goal_dist_end":0.01317,"object_to_goal_dist_start":0.10733,"object_z_max":0.25119,"peak_contact_force":0.11839,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5841.0,"raw_peak_contact_force":0.3513,"subtask_id":"reach_goal","tcp_end":[0.62141,0.16861,0.18693],"tcp_start":[0.61398,0.15882,0.2788],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64773,"average_solve_count":440.0,"average_success_count":440.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.14353,"descend_approach.approach_speed":0.06585,"descend_to_grasp.descend_speed":0.02551,"descend_to_grasp.grasp_height":0.02,"descend_to_place.place_height_offset":0.02757,"descend_to_place.place_speed":0.01531,"lift_object.lift_height":0.13376,"lift_object.lift_speed":0.04129,"transport_to_goal.arc_height":0.05951,"transport_to_goal.transport_height":0.11524,"transport_to_goal.transport_speed":0.04637},"optimized_scores":{"best_composite_score":0.29233,"best_fitness_score":0.96233,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47957,0.04637,-0.00155],"force_p95":0.36989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3945,"mean_force":0.13954,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46982,0.04661,0.04795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6707.0,"contact_point_centroid":[0.47275,0.06564,0.0927],"force_p95":0.08375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26921,"mean_force":0.05441,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47247,0.04663,0.09122]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1945.0,"contact_point_centroid":[0.57415,0.23323,0.30336],"force_p95":0.131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26332,"mean_force":0.08974,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57186,0.21443,0.3062]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2119.0,"contact_point_centroid":[0.57281,0.19608,0.30457],"force_p95":0.10579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25749,"mean_force":0.07448,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57176,0.21425,0.30708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5594.0,"contact_point_centroid":[0.47183,0.02744,0.09318],"force_p95":0.08996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23921,"mean_force":0.0621,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47253,0.04664,0.09187]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04859,-0.00216],"force_p95":0.16771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22751,"mean_force":0.13445,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47178,0.04682,0.04793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18736.0,"contact_point_centroid":[0.50572,0.11789,0.25301],"force_p95":0.08485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1491,"mean_force":0.05375,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50517,0.09888,0.25244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18385.0,"contact_point_centroid":[0.50698,0.08427,0.25848],"force_p95":0.08693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14223,"mean_force":0.05467,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50776,0.10333,0.25814]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49129,0.0188,0.24704]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47924,0.04341,0.12233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4330.0,"contact_point_centroid":[0.4703,0.0275,0.04823],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11647,"mean_force":0.04965,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47069,0.04671,0.04679]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.47054,0.06593,0.04832],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0746,"mean_force":0.04218,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47069,0.04671,0.0468]}],"total_contact_groups":12},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58073,0.22266,0.23888],"final_tcp_position":[0.57643,0.22253,0.27031],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":23.10571,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":23.06012,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48293,0.03968,0.19109],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":23.10571,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47836,0.04744,0.05484],"tcp_start":[0.48293,0.03968,0.19109],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04734,0.02542],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29127,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16341,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11427.0,"raw_peak_contact_force":0.22751,"subtask_id":"reach_grasp_height","tcp_end":[0.47066,0.04671,0.04676],"tcp_start":[0.47836,0.04744,0.05484],"tcp_to_object_dist_end":0.0245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.48574,0.04728,0.11645],"object_pos_start":[0.48268,0.04734,0.02542],"object_to_goal_dist_end":0.23498,"object_to_goal_dist_start":0.29127,"object_z_max":0.11617,"peak_contact_force":0.0874,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12393.0,"raw_peak_contact_force":0.3945,"subtask_id":"lift_clearance","tcp_end":[0.4775,0.04689,0.13987],"tcp_start":[0.47066,0.04671,0.04676],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57196,0.20881,0.30639],"object_pos_start":[0.48574,0.04728,0.11645],"object_to_goal_dist_end":0.07913,"object_to_goal_dist_start":0.23498,"object_z_max":0.30637,"peak_contact_force":0.11313,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37121.0,"raw_peak_contact_force":0.1491,"subtask_id":"transport_above","tcp_end":[0.56917,0.20844,0.33618],"tcp_start":[0.4775,0.04689,0.13987],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.58073,0.22266,0.23888],"object_pos_start":[0.57196,0.20881,0.30639],"object_to_goal_dist_end":0.0105,"object_to_goal_dist_start":0.07913,"object_z_max":0.30639,"peak_contact_force":0.13681,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4064.0,"raw_peak_contact_force":0.26332,"subtask_id":"reach_goal","tcp_end":[0.57643,0.22253,0.27031],"tcp_start":[0.56917,0.20844,0.33618],"tcp_to_object_dist_end":0.03172,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.51389,"average_solve_count":576.0,"average_success_count":576.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.10266,"descend_approach.approach_speed":0.02966,"descend_to_grasp.descend_speed":0.01063,"descend_to_grasp.grasp_height":0.0224,"descend_to_place.place_height_offset":0.03984,"descend_to_place.place_speed":0.01505,"lift_object.lift_height":0.19986,"lift_object.lift_speed":0.03381,"transport_to_goal.arc_height":0.08613,"transport_to_goal.transport_height":0.1136,"transport_to_goal.transport_speed":0.02525},"optimized_scores":{"best_composite_score":0.29159,"best_fitness_score":0.96159,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1174.0,"contact_point_centroid":[0.60843,0.2312,0.29221],"force_p95":0.13758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46788,"mean_force":0.1221,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60353,0.21305,0.29519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.60831,0.1953,0.29151],"force_p95":0.1304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44593,"mean_force":0.10525,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60358,0.21319,0.2946]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.53374,-0.02045,-0.0015],"force_p95":0.33539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35624,"mean_force":0.1412,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52179,-0.02064,0.04729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11346.0,"contact_point_centroid":[0.5261,-0.00151,0.12665],"force_p95":0.07907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23813,"mean_force":0.05568,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52574,-0.02065,0.12514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12217.0,"contact_point_centroid":[0.52611,-0.03974,0.12366],"force_p95":0.07744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23744,"mean_force":0.05245,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52549,-0.02065,0.12198]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02125,-0.00206],"force_p95":0.14032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18175,"mean_force":0.12741,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52404,-0.02068,0.04785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17013.0,"contact_point_centroid":[0.5544,0.03128,0.29693],"force_p95":0.10449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16471,"mean_force":0.05759,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55276,0.04996,0.29714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14462.0,"contact_point_centroid":[0.55354,0.06562,0.29448],"force_p95":0.12425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15148,"mean_force":0.06849,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5517,0.04667,0.29497]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.5127,-0.00867,0.22716]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52815,-0.01947,0.10274]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4351.0,"contact_point_centroid":[0.52383,-0.00147,0.04815],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11596,"mean_force":0.04944,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52284,-0.02065,0.04645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4906.0,"contact_point_centroid":[0.52373,-0.0398,0.04794],"force_p95":0.0698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08431,"mean_force":0.04458,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52285,-0.02065,0.04645]}],"total_contact_groups":12},"final_pose_error":0.0146,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61144,0.22072,0.225],"final_tcp_position":[0.60602,0.22117,0.25955],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.46788,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52837,-0.01825,0.15011],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53113,-0.0208,0.05627],"tcp_start":[0.52837,-0.01825,0.15011],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02082,0.02577],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13886,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11057.0,"raw_peak_contact_force":0.18175,"subtask_id":"reach_grasp_height","tcp_end":[0.52281,-0.02065,0.04641],"tcp_start":[0.53113,-0.0208,0.05627],"tcp_to_object_dist_end":0.02502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.54013,-0.02093,0.18132],"object_pos_start":[0.53695,-0.02082,0.02577],"object_to_goal_dist_end":0.25971,"object_to_goal_dist_start":0.31649,"object_z_max":0.18107,"peak_contact_force":0.0768,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23662.0,"raw_peak_contact_force":0.35624,"subtask_id":"lift_clearance","tcp_end":[0.53258,-0.02073,0.20636],"tcp_start":[0.52281,-0.02065,0.04641],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60855,0.2059,0.29293],"object_pos_start":[0.54013,-0.02093,0.18132],"object_to_goal_dist_end":0.08829,"object_to_goal_dist_start":0.25971,"object_z_max":0.31749,"peak_contact_force":0.13017,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31475.0,"raw_peak_contact_force":0.16471,"subtask_id":"transport_above","tcp_end":[0.60267,0.20698,0.3254],"tcp_start":[0.53258,-0.02073,0.20636],"tcp_to_object_dist_end":0.03301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.61144,0.22072,0.225],"object_pos_start":[0.60855,0.2059,0.29293],"object_to_goal_dist_end":0.01898,"object_to_goal_dist_start":0.08829,"object_z_max":0.29293,"peak_contact_force":0.13741,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2554.0,"raw_peak_contact_force":0.46788,"subtask_id":"reach_goal","tcp_end":[0.60602,0.22117,0.25955],"tcp_start":[0.60267,0.20698,0.3254],"tcp_to_object_dist_end":0.03498,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```