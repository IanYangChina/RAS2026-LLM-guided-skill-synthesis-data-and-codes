## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.2857 | 0.90 | ❌ rejected |
| 11 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3350 | 1.00 | ✅ accepted |
| 10 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.1398 | 0.70 | ❌ rejected |
| 9 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2118 | 0.18 | ❌ rejected |
| 8 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.3363 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.336) — your mutation base

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
  offset:
  - 0.0
  - 0.0
  - 0.01
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
    tolerance: 0.015
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
    tolerance: 0.025
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
    - 0.1
    tolerance: 0.1
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.04
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
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_height_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.1
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.336
- **task_score** (E): 1.000
- **fitness_score**: 0.956  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1663 |
| descend_to_grasp | 1.00 | 1.00 | 0.0791 |
| grasp_object | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1095 |
| transport_to_goal | 0.00 | 1.00 | 0.1640 |
| descend_to_place | 1.00 | 1.00 | 0.0662 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.139) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 9.264 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.139)→(0.505, 0.022, 0.060) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 13.987 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.505, 0.022, 0.060)→(0.497, 0.021, 0.051) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 37.333 | 0.172 | 0.216 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.021, 0.051)→(0.505, 0.021, 0.160) | (0.511, 0.021, 0.025)→(0.513, 0.022, 0.131) | 0.274→0.224 | 1.00 / 25.333 | 0.118 | 0.312 |
| transport_to_goal | approach | 0.00 / step_budget | (0.505, 0.021, 0.160)→(0.574, 0.140, 0.243) | (0.513, 0.022, 0.131)→(0.580, 0.139, 0.214) | 0.224→0.080 | 1.00 / 29.000 | 0.123 | 0.190 |
| descend_to_place | descend | 1.00 / step_budget | (0.574, 0.140, 0.243)→(0.597, 0.194, 0.218) | (0.580, 0.139, 0.214)→(0.603, 0.194, 0.187) | 0.080→0.019 | 1.00 / 24.667 | 0.130 | 0.459 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.043
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.575
- phase_breakdown.reach_grasp_height_score: 0.719
- phase_breakdown.lift_clearance_score: 0.514
- phase_breakdown.reach_goal_score: 0.653
- phase_breakdown.transport_above_score: 0.166
- phase_breakdown.reach_approach_score: 0.577
- grasp_place_fitness: 0.957

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.957
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.336
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: descend_to_place.place_speed
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.56738,"average_solve_count":423.0,"average_success_count":423.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.10808,"descend_approach.approach_speed":0.05848,"descend_to_grasp.descend_speed":0.02684,"descend_to_grasp.grasp_height":0.02,"descend_to_place.place_height_offset":0.01656,"descend_to_place.place_speed":0.01319,"lift_object.lift_height":0.14604,"lift_object.lift_speed":0.02745,"transport_to_goal.transport_height":0.1172,"transport_to_goal.transport_speed":0.06267},"optimized_scores":{"best_composite_score":0.33666,"best_fitness_score":0.95666,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":3171.0,"contact_point_centroid":[0.59683,0.15046,0.18531],"force_p95":0.12271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45951,"mean_force":0.06991,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59426,0.13216,0.18591]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2544.0,"contact_point_centroid":[0.59532,0.11313,0.18431],"force_p95":0.13777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35576,"mean_force":0.08207,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59408,0.1319,0.18619]},{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.50964,0.03732,-0.00177],"force_p95":0.2785,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30294,"mean_force":0.12948,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4982,0.03757,0.05146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3765.0,"contact_point_centroid":[0.50149,0.01844,0.08933],"force_p95":0.12083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2745,"mean_force":0.0794,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5008,0.03756,0.09087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5842.0,"contact_point_centroid":[0.50081,0.05612,0.09543],"force_p95":0.0893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2337,"mean_force":0.05332,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50126,0.03757,0.09535]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03962,-0.00218],"force_p95":0.17593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22333,"mean_force":0.13579,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50035,0.03776,0.05183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1542.0,"contact_point_centroid":[0.5337,0.08254,0.16753],"force_p95":0.12981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18507,"mean_force":0.0656,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53302,0.06419,0.16746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.53487,0.04804,0.1686],"force_p95":0.14601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17993,"mean_force":0.09131,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53595,0.06714,0.16972]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50288,0.01609,0.22965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3437.0,"contact_point_centroid":[0.50169,0.01852,0.05009],"force_p95":0.10903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13199,"mean_force":0.06308,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49921,0.03767,0.05056]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50614,0.0358,0.10865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4863.0,"contact_point_centroid":[0.49998,0.05646,0.05086],"force_p95":0.07502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07854,"mean_force":0.04393,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49922,0.03767,0.05057]}],"total_contact_groups":12},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62139,0.15909,0.13288],"final_tcp_position":[0.61365,0.15824,0.16253],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":27.96025,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50745,0.03361,0.15636],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":27.96025,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50732,0.0383,0.05982],"tcp_start":[0.50745,0.03361,0.15636],"tcp_to_object_dist_end":0.03422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03815,0.02526],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21365,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17641,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10100.0,"raw_peak_contact_force":0.22333,"subtask_id":"reach_grasp_height","tcp_end":[0.49918,0.03766,0.05053],"tcp_start":[0.50732,0.0383,0.05982],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.51533,0.03876,0.11962],"object_pos_start":[0.51248,0.03815,0.02526],"object_to_goal_dist_end":0.17645,"object_to_goal_dist_start":0.21365,"object_z_max":0.11927,"peak_contact_force":0.12057,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9712.0,"raw_peak_contact_force":0.30294,"subtask_id":"lift_clearance","tcp_end":[0.50689,0.03776,0.14729],"tcp_start":[0.49918,0.03766,0.05053],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.58451,0.10969,0.17531],"object_pos_start":[0.51533,0.03876,0.11962],"object_to_goal_dist_end":0.08197,"object_to_goal_dist_start":0.17645,"object_z_max":0.17432,"peak_contact_force":0.12565,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2718.0,"raw_peak_contact_force":0.18507,"subtask_id":"transport_above","tcp_end":[0.57815,0.10991,0.20372],"tcp_start":[0.50689,0.03776,0.14729],"tcp_to_object_dist_end":0.02912,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.62139,0.15909,0.13288],"object_pos_start":[0.58451,0.10969,0.17531],"object_to_goal_dist_end":0.01913,"object_to_goal_dist_start":0.08197,"object_z_max":0.18074,"peak_contact_force":0.13478,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5715.0,"raw_peak_contact_force":0.45951,"subtask_id":"reach_goal","tcp_end":[0.61365,0.15824,0.16253],"tcp_start":[0.57815,0.10991,0.20372],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5375,"average_solve_count":480.0,"average_success_count":480.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.07525,"descend_approach.approach_speed":0.05875,"descend_to_grasp.descend_speed":0.01336,"descend_to_grasp.grasp_height":0.02002,"descend_to_place.place_height_offset":0.02368,"descend_to_place.place_speed":0.03,"lift_object.lift_height":0.16112,"lift_object.lift_speed":0.01653,"transport_to_goal.transport_height":0.12653,"transport_to_goal.transport_speed":0.04571},"optimized_scores":{"best_composite_score":0.33606,"best_fitness_score":0.95606,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":2177.0,"contact_point_centroid":[0.56398,0.20864,0.27153],"force_p95":0.14518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4,"mean_force":0.07795,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56344,0.18992,0.27238]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.48028,0.04619,-0.00179],"force_p95":0.27251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29559,"mean_force":0.12827,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46956,0.04598,0.05245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3609.0,"contact_point_centroid":[0.47183,0.02713,0.0993],"force_p95":0.12176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26306,"mean_force":0.08497,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47228,0.04602,0.10148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5247.0,"contact_point_centroid":[0.47235,0.06454,0.09885],"force_p95":0.10832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24175,"mean_force":0.06357,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4721,0.04601,0.09959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2208.0,"contact_point_centroid":[0.56298,0.1712,0.27165],"force_p95":0.11995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23855,"mean_force":0.06567,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56338,0.18974,0.27257]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04854,-0.0022],"force_p95":0.18313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23667,"mean_force":0.13711,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47168,0.0462,0.05277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.50843,0.11571,0.21122],"force_p95":0.11685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18854,"mean_force":0.07219,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50947,0.09725,0.21284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1646.0,"contact_point_centroid":[0.50821,0.07917,0.21193],"force_p95":0.12586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18694,"mean_force":0.08675,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50992,0.09798,0.2136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2454.0,"contact_point_centroid":[0.47175,0.0271,0.04939],"force_p95":0.11036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13963,"mean_force":0.08257,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4706,0.0461,0.05164]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49028,0.02045,0.21343]},{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47878,0.04432,0.09389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4907.0,"contact_point_centroid":[0.47105,0.06483,0.05161],"force_p95":0.08023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08392,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47061,0.0461,0.05165]}],"total_contact_groups":12},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57854,0.21153,0.22568],"final_tcp_position":[0.57233,0.21163,0.25566],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":27.54808,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":27.54808,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48144,0.04238,0.12414],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":13.87676,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":728.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47834,0.04681,0.0599],"tcp_start":[0.48144,0.04238,0.12414],"tcp_to_object_dist_end":0.03421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04675,0.02528],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29173,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17794,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9161.0,"raw_peak_contact_force":0.23667,"subtask_id":"reach_grasp_height","tcp_end":[0.47057,0.04609,0.05161],"tcp_start":[0.47834,0.04681,0.0599],"tcp_to_object_dist_end":0.02899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.48371,0.04712,0.13294],"object_pos_start":[0.48271,0.04675,0.02528],"object_to_goal_dist_end":0.22843,"object_to_goal_dist_start":0.29173,"object_z_max":0.13258,"peak_contact_force":0.11922,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8966.0,"raw_peak_contact_force":0.29559,"subtask_id":"lift_clearance","tcp_end":[0.47769,0.04631,0.1622],"tcp_start":[0.47057,0.04609,0.05161],"tcp_to_object_dist_end":0.02988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.5586,0.16709,0.2554],"object_pos_start":[0.48371,0.04712,0.13294],"object_to_goal_dist_end":0.07055,"object_to_goal_dist_start":0.22843,"object_z_max":0.2541,"peak_contact_force":0.10745,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3566.0,"raw_peak_contact_force":0.18854,"subtask_id":"transport_above","tcp_end":[0.55392,0.16774,0.28474],"tcp_start":[0.47769,0.04631,0.1622],"tcp_to_object_dist_end":0.02972,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.57854,0.21153,0.22568],"object_pos_start":[0.5586,0.16709,0.2554],"object_to_goal_dist_end":0.01829,"object_to_goal_dist_start":0.07055,"object_z_max":0.26163,"peak_contact_force":0.12767,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4385.0,"raw_peak_contact_force":0.4,"subtask_id":"reach_goal","tcp_end":[0.57233,0.21163,0.25566],"tcp_start":[0.55392,0.16774,0.28474],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88347,"average_solve_count":369.0,"average_success_count":369.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.08885,"descend_approach.approach_speed":0.05122,"descend_to_grasp.descend_speed":0.02868,"descend_to_grasp.grasp_height":0.02104,"descend_to_place.place_height_offset":0.03614,"descend_to_place.place_speed":0.02224,"lift_object.lift_height":0.16944,"lift_object.lift_speed":0.0464,"transport_to_goal.transport_height":0.08126,"transport_to_goal.transport_speed":0.0676},"optimized_scores":{"best_composite_score":0.33618,"best_fitness_score":0.95618,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1929.0,"contact_point_centroid":[0.60037,0.19647,0.23513],"force_p95":0.17138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51831,"mean_force":0.10553,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59604,0.17816,0.23745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2104.0,"contact_point_centroid":[0.60022,0.16027,0.23608],"force_p95":0.13616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44781,"mean_force":0.09643,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5961,0.17831,0.23752]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.53402,-0.01977,-0.00164],"force_p95":0.30592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33757,"mean_force":0.12369,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5215,-0.02044,0.05149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3958.0,"contact_point_centroid":[0.52669,-0.00146,0.10154],"force_p95":0.12729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31542,"mean_force":0.08776,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52481,-0.02044,0.10291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6236.0,"contact_point_centroid":[0.52551,-0.03888,0.10625],"force_p95":0.10728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24286,"mean_force":0.06149,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5251,-0.02044,0.10621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1893.0,"contact_point_centroid":[0.55522,0.02571,0.1974],"force_p95":0.13118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19638,"mean_force":0.07753,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55477,0.04427,0.19804]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02131,-0.0021],"force_p95":0.15508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18671,"mean_force":0.13009,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52359,-0.02049,0.05182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1229.0,"contact_point_centroid":[0.55709,0.06337,0.1954],"force_p95":0.13618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18467,"mean_force":0.09435,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55501,0.04491,0.19832]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51303,-0.00887,0.21971]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52846,-0.01947,0.09899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4311.0,"contact_point_centroid":[0.52348,-0.00128,0.05072],"force_p95":0.09286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11743,"mean_force":0.05316,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5224,-0.02046,0.05043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4921.0,"contact_point_centroid":[0.52332,-0.03941,0.05073],"force_p95":0.06975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07284,"mean_force":0.04334,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.02046,0.05043]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61036,0.21002,0.2024],"final_tcp_position":[0.60381,0.21113,0.23476],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51831,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52861,-0.01844,0.13658],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53079,-0.02061,0.06052],"tcp_start":[0.52861,-0.01844,0.13658],"tcp_to_object_dist_end":0.03507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53698,-0.02059,0.02545],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31648,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.16126,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11032.0,"raw_peak_contact_force":0.18671,"subtask_id":"reach_grasp_height","tcp_end":[0.52238,-0.02046,0.0504],"tcp_start":[0.53079,-0.02061,0.06052],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.53933,-0.02131,0.14123],"object_pos_start":[0.53698,-0.02059,0.02545],"object_to_goal_dist_end":0.2673,"object_to_goal_dist_start":0.31648,"object_z_max":0.14088,"peak_contact_force":0.11432,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10279.0,"raw_peak_contact_force":0.33757,"subtask_id":"lift_clearance","tcp_end":[0.53168,-0.02049,0.17068],"tcp_start":[0.52238,-0.02046,0.0504],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.59787,0.14046,0.2117],"object_pos_start":[0.53933,-0.02131,0.14123],"object_to_goal_dist_end":0.08828,"object_to_goal_dist_start":0.2673,"object_z_max":0.21093,"peak_contact_force":0.13553,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3122.0,"raw_peak_contact_force":0.19638,"subtask_id":"transport_above","tcp_end":[0.58973,0.14281,0.24187],"tcp_start":[0.53168,-0.02049,0.17068],"tcp_to_object_dist_end":0.03134,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.61036,0.21002,0.2024],"object_pos_start":[0.59787,0.14046,0.2117],"object_to_goal_dist_end":0.01843,"object_to_goal_dist_start":0.08828,"object_z_max":0.21459,"peak_contact_force":0.12753,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4033.0,"raw_peak_contact_force":0.51831,"subtask_id":"reach_goal","tcp_end":[0.60381,0.21113,0.23476],"tcp_start":[0.58973,0.14281,0.24187],"tcp_to_object_dist_end":0.03304,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```