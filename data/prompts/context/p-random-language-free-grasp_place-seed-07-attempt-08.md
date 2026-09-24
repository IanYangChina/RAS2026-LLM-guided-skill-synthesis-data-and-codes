## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5451 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2138 | 0.77 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1507 | 0.33 | ❌ rejected |

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

## Current Skill (Q=0.545) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_reach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_goal
  weight: 0.2
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: none
  subtask_id: grasp_reach
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
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: grasp_reach
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_clear
- id: transport
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
    - 0.1
    orientation:
      mode: none
  parameters:
    transport_overhead:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
- id: descend_place
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
      mode: none
  parameters:
    place_descent_z:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=none
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - transport_overhead: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - place_descent_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.545
- **task_score** (E): 1.000
- **fitness_score**: 0.965  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1683 |
| descend_grasp | 1.00 | 1.00 | 0.0847 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 0.00 | 1.00 | 0.1817 |
| transport | 0.67 | 1.00 | 0.2097 |
| descend_place | 1.00 | 1.00 | 0.0978 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.053) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.053)→(0.497, 0.022, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 45.667 | 0.147 | 0.184 |
| lift | lift | 0.00 / step_budget | (0.497, 0.022, 0.044)→(0.508, 0.022, 0.225) | (0.511, 0.022, 0.026)→(0.525, 0.022, 0.209) | 0.273→0.214 | 1.00 / 40.667 | 0.086 | 0.482 |
| transport | approach | 0.67 / step_budget | (0.508, 0.022, 0.225)→(0.593, 0.182, 0.322) | (0.525, 0.022, 0.209)→(0.598, 0.185, 0.296) | 0.214→0.108 | 1.00 / 34.000 | 0.098 | 0.279 |
| descend_place | descend | 1.00 / step_budget | (0.593, 0.182, 0.322)→(0.602, 0.205, 0.229) | (0.598, 0.185, 0.296)→(0.602, 0.207, 0.201) | 0.108→0.010 | 1.00 / 32.667 | 0.109 | 0.284 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.485
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.504
- phase_breakdown.place_goal_score: 0.490
- phase_breakdown.approach_goal_score: 0.291
- phase_breakdown.grasp_reach_score: 0.639
- phase_breakdown.lift_clear_score: 0.280
- phase_breakdown.approach_object_score: 0.822
- grasp_place_fitness: 0.967

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.967
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.545
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85955,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06334,"descend_place.place_descent_z":0.01768,"lift.lift_height":0.27749,"lift.lift_tolerance":0.07423,"transport.transport_overhead":0.16067,"transport.transport_speed":0.46573},"optimized_scores":{"best_composite_score":0.54541,"best_fitness_score":0.96541,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.50969,0.03898,-0.0016],"force_p95":0.44814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49364,"mean_force":0.28783,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49792,0.03844,0.04459]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6255.0,"contact_point_centroid":[0.61352,0.18378,0.23437],"force_p95":0.08144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31665,"mean_force":0.05313,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61856,0.16571,0.23278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3122.0,"contact_point_centroid":[0.50033,0.05775,0.12813],"force_p95":0.12188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30887,"mean_force":0.06145,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50156,0.03853,0.12415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3559.0,"contact_point_centroid":[0.50247,0.0193,0.12693],"force_p95":0.11859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2999,"mean_force":0.05646,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5016,0.03853,0.12477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5280.0,"contact_point_centroid":[0.62173,0.14684,0.23132],"force_p95":0.09757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26191,"mean_force":0.06488,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61859,0.16574,0.23238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19502.0,"contact_point_centroid":[0.56316,0.07997,0.25942],"force_p95":0.08447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2576,"mean_force":0.05393,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56084,0.09899,0.25794]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19606.0,"contact_point_centroid":[0.56263,0.12329,0.26362],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22584,"mean_force":0.05261,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56569,0.10454,0.26079]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0398,-0.00211],"force_p95":0.15339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20062,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03866,0.04489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50049,0.01931,0.04578],"force_p95":0.06867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1682,"mean_force":0.04016,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04353]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50257,0.01776,0.21865]},{"body_a":"world","body_b":"grasp_target","contact_count":2908.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50611,0.03798,0.08435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.49819,0.05778,0.04806],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07633,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04353]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62354,0.17238,0.14426],"final_tcp_position":[0.62245,0.17016,0.17088],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.49364,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50749,0.0363,0.13769],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2908.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50736,0.03922,0.05268],"tcp_start":[0.50749,0.0363,0.13769],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03926,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15276,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12504.0,"raw_peak_contact_force":0.20062,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.03855,0.0435],"tcp_start":[0.50736,0.03922,0.05268],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.52776,0.04008,0.21376],"object_pos_start":[0.51251,0.03926,0.0256],"object_to_goal_dist_end":0.17952,"object_to_goal_dist_start":0.21274,"object_z_max":0.21235,"peak_contact_force":0.08303,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6744.0,"raw_peak_contact_force":0.49364,"subtask_id":"lift_clear","tcp_end":[0.51018,0.03897,0.22943],"tcp_start":[0.49917,0.03855,0.0435],"tcp_to_object_dist_end":0.02357,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62231,0.16449,0.26803],"object_pos_start":[0.52776,0.04008,0.21376],"object_to_goal_dist_end":0.12338,"object_to_goal_dist_start":0.17952,"object_z_max":0.26795,"peak_contact_force":0.08424,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39108.0,"raw_peak_contact_force":0.2576,"subtask_id":"approach_goal","tcp_end":[0.61669,0.16214,0.29186],"tcp_start":[0.51018,0.03897,0.22943],"tcp_to_object_dist_end":0.02459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.62354,0.17238,0.14426],"object_pos_start":[0.62231,0.16449,0.26803],"object_to_goal_dist_end":0.0041,"object_to_goal_dist_start":0.12338,"object_z_max":0.26803,"peak_contact_force":0.09615,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11535.0,"raw_peak_contact_force":0.31665,"subtask_id":"place_goal","tcp_end":[0.62245,0.17016,0.17088],"tcp_start":[0.61669,0.16214,0.29186],"tcp_to_object_dist_end":0.02673,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02083,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09877,"descend_place.place_descent_z":0.03748,"lift.lift_height":0.24806,"lift.lift_tolerance":0.0715,"transport.transport_overhead":0.14255,"transport.transport_speed":0.44116},"optimized_scores":{"best_composite_score":0.54296,"best_fitness_score":0.96296,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.47951,0.04755,-0.00162],"force_p95":0.42242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45457,"mean_force":0.2748,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46863,0.04718,0.04689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18373.0,"contact_point_centroid":[0.52448,0.10578,0.27031],"force_p95":0.0913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29707,"mean_force":0.05742,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52111,0.12462,0.26996]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2591.0,"contact_point_centroid":[0.47062,0.06642,0.11687],"force_p95":0.13706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28747,"mean_force":0.06618,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47179,0.04727,0.11396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3394.0,"contact_point_centroid":[0.56647,0.2344,0.31251],"force_p95":0.09578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28326,"mean_force":0.06242,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57322,0.21722,0.31293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2743.0,"contact_point_centroid":[0.47373,0.02816,0.11597],"force_p95":0.14057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27945,"mean_force":0.06508,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4719,0.04727,0.11504]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19542.0,"contact_point_centroid":[0.52059,0.14888,0.27719],"force_p95":0.07906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26381,"mean_force":0.05259,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52438,0.13039,0.27522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2582.0,"contact_point_centroid":[0.57705,0.19855,0.31054],"force_p95":0.12132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23366,"mean_force":0.08239,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5732,0.21718,0.3131]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04878,-0.00212],"force_p95":0.156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20118,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47098,0.04742,0.04706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.47165,0.02812,0.04666],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15947,"mean_force":0.04362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04583]},{"body_a":"world","body_b":"grasp_target","contact_count":2048.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48923,0.02172,0.21917]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47746,0.04627,0.09195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46884,0.06652,0.04944],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07757,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04583]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57858,0.22738,0.24562],"final_tcp_position":[0.57729,0.2245,0.27566],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.45457,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2048.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48016,0.04446,0.13845],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47771,0.04808,0.05413],"tcp_start":[0.48016,0.04446,0.13845],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04813,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15504,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.20118,"subtask_id":"grasp_reach","tcp_end":[0.46976,0.0473,0.0458],"tcp_start":[0.47771,0.04808,0.05413],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.4956,0.04895,0.18437],"object_pos_start":[0.48274,0.04813,0.02556],"object_to_goal_dist_end":0.20478,"object_to_goal_dist_start":0.29066,"object_z_max":0.183,"peak_contact_force":0.08983,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5394.0,"raw_peak_contact_force":0.45457,"subtask_id":"lift_clear","tcp_end":[0.47972,0.04775,0.20273],"tcp_start":[0.46976,0.0473,0.0458],"tcp_to_object_dist_end":0.0243,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57508,0.21397,0.32146],"object_pos_start":[0.4956,0.04895,0.18437],"object_to_goal_dist_end":0.09243,"object_to_goal_dist_start":0.20478,"object_z_max":0.32134,"peak_contact_force":0.11122,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37915.0,"raw_peak_contact_force":0.29707,"subtask_id":"approach_goal","tcp_end":[0.5705,0.211,0.34933],"tcp_start":[0.47972,0.04775,0.20273],"tcp_to_object_dist_end":0.0284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.57858,0.22738,0.24562],"object_pos_start":[0.57508,0.21397,0.32146],"object_to_goal_dist_end":0.01556,"object_to_goal_dist_start":0.09243,"object_z_max":0.32148,"peak_contact_force":0.11813,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5976.0,"raw_peak_contact_force":0.28326,"subtask_id":"place_goal","tcp_end":[0.57729,0.2245,0.27566],"tcp_start":[0.5705,0.211,0.34933],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52232,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03258,"descend_place.place_descent_z":0.03221,"lift.lift_height":0.27598,"lift.lift_tolerance":0.05863,"transport.transport_overhead":0.15083,"transport.transport_speed":0.25979},"optimized_scores":{"best_composite_score":0.54684,"best_fitness_score":0.96684,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.53345,-0.02138,-0.00151],"force_p95":0.43819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49896,"mean_force":0.25437,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52202,-0.02105,0.04331]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4293.0,"contact_point_centroid":[0.52702,-0.00215,0.13605],"force_p95":0.09857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32022,"mean_force":0.05775,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52621,-0.02121,0.1342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3642.0,"contact_point_centroid":[0.5258,-0.04043,0.13807],"force_p95":0.10447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31185,"mean_force":0.06466,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52629,-0.02121,0.1353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16722.0,"contact_point_centroid":[0.56402,0.05443,0.28211],"force_p95":0.1066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28381,"mean_force":0.06728,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56059,0.07326,0.28098]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5854.0,"contact_point_centroid":[0.59061,0.212,0.28388],"force_p95":0.09783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2519,"mean_force":0.05618,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59718,0.19447,0.28281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20679.0,"contact_point_centroid":[0.56013,0.09651,0.28505],"force_p95":0.08283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22942,"mean_force":0.04936,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56208,0.07808,0.28312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.60231,0.17638,0.28025],"force_p95":0.116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21492,"mean_force":0.07399,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59725,0.19473,0.28238]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15067,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52457,-0.02108,0.04379]},{"body_a":"world","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51365,-0.00964,0.218]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52959,-0.02054,0.08471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52405,-0.00198,0.04433],"force_p95":0.06854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10083,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52255,-0.04032,0.04526],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.05164,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60297,0.22244,0.2123],"final_tcp_position":[0.60503,0.21974,0.2418],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.49896,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53013,-0.01965,0.13674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.5317,-0.02119,0.05219],"tcp_start":[0.53013,-0.01965,0.13674],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0215,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1335,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11293.0,"raw_peak_contact_force":0.15067,"subtask_id":"grasp_reach","tcp_end":[0.52328,-0.02106,0.04228],"tcp_start":[0.5317,-0.02119,0.05219],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.55134,-0.02202,0.22867],"object_pos_start":[0.53692,-0.0215,0.02586],"object_to_goal_dist_end":0.25752,"object_to_goal_dist_start":0.31698,"object_z_max":0.2276,"peak_contact_force":0.08445,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7998.0,"raw_peak_contact_force":0.49896,"subtask_id":"lift_clear","tcp_end":[0.53378,-0.0214,0.24362],"tcp_start":[0.52328,-0.02106,0.04228],"tcp_to_object_dist_end":0.02306,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59766,0.17522,0.2996],"object_pos_start":[0.55134,-0.02202,0.22867],"object_to_goal_dist_end":0.10686,"object_to_goal_dist_start":0.25752,"object_z_max":0.29952,"peak_contact_force":0.09783,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37401.0,"raw_peak_contact_force":0.28381,"subtask_id":"approach_goal","tcp_end":[0.59129,0.17178,0.32492],"tcp_start":[0.53378,-0.0214,0.24362],"tcp_to_object_dist_end":0.02634,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.60297,0.22244,0.2123],"object_pos_start":[0.59766,0.17522,0.2996],"object_to_goal_dist_end":0.01029,"object_to_goal_dist_start":0.10686,"object_z_max":0.2996,"peak_contact_force":0.11207,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.2519,"subtask_id":"place_goal","tcp_end":[0.60503,0.21974,0.2418],"tcp_start":[0.59129,0.17178,0.32492],"tcp_to_object_dist_end":0.0297,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```