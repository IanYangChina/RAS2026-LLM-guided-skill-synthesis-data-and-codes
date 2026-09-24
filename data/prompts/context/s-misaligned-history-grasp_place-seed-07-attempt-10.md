## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.1398 | 0.70 | ❌ rejected |
| 9 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2118 | 0.18 | ❌ rejected |
| 8 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2263 | 0.87 | ❌ rejected |
| 7 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2924 | 1.00 | ❌ rejected |
| 6 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.3350 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.335) — your mutation base

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
  - 0.03
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
    tolerance: 0.07
    orientation:
      mode: keep_current
  parameters:
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
    tolerance: 0.03
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
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.07
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.03], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.335
- **task_score** (E): 1.000
- **fitness_score**: 0.955  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1430 |
| descend_to_grasp | 1.00 | 1.00 | 0.1020 |
| grasp_object | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1159 |
| transport_to_goal | 0.00 | 1.00 | 0.1939 |
| descend_to_place | 1.00 | 1.00 | 0.0567 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.163) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.163)→(0.506, 0.022, 0.061) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.061)→(0.498, 0.021, 0.052) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 32.333 | 0.165 | 0.214 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.052)→(0.506, 0.021, 0.168) | (0.511, 0.021, 0.025)→(0.512, 0.022, 0.138) | 0.274→0.222 | 1.00 / 24.333 | 0.120 | 0.294 |
| transport_to_goal | approach | 0.00 / step_budget | (0.506, 0.021, 0.168)→(0.582, 0.163, 0.272) | (0.512, 0.022, 0.138)→(0.587, 0.162, 0.241) | 0.222→0.070 | 1.00 / 25.333 | 0.118 | 0.195 |
| descend_to_place | descend | 1.00 / step_budget | (0.582, 0.163, 0.272)→(0.595, 0.191, 0.225) | (0.587, 0.162, 0.241)→(0.603, 0.191, 0.193) | 0.070→0.020 | 1.00 / 18.000 | 0.135 | 0.483 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.030
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.629
- phase_breakdown.reach_grasp_height_score: 0.714
- phase_breakdown.lift_clearance_score: 0.536
- phase_breakdown.reach_goal_score: 0.603
- phase_breakdown.transport_above_score: 0.261
- phase_breakdown.reach_approach_score: 0.859
- grasp_place_fitness: 0.957

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.957
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.335
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.352


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.53425,"average_solve_count":438.0,"average_success_count":438.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.07945,"descend_approach.approach_speed":0.08683,"descend_to_grasp.descend_speed":0.02565,"descend_to_grasp.grasp_height":0.02,"descend_to_place.place_height_offset":0.01034,"descend_to_place.place_speed":0.01378,"lift_object.lift_height":0.14821,"lift_object.lift_speed":0.02026,"transport_to_goal.transport_height":0.1046,"transport_to_goal.transport_speed":0.04802},"optimized_scores":{"best_composite_score":0.33674,"best_fitness_score":0.95674,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1721.0,"contact_point_centroid":[0.60075,0.15653,0.19623],"force_p95":0.12418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48706,"mean_force":0.07413,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59768,0.1381,0.19666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1242.0,"contact_point_centroid":[0.59983,0.11935,0.19413],"force_p95":0.13855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32081,"mean_force":0.09396,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59762,0.13801,0.1968]},{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.51001,0.03762,-0.00184],"force_p95":0.27087,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28841,"mean_force":0.1253,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49789,0.03742,0.05111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3847.0,"contact_point_centroid":[0.50154,0.01835,0.08915],"force_p95":0.12152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25252,"mean_force":0.08027,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50053,0.03744,0.09045]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03963,-0.0022],"force_p95":0.1796,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22641,"mean_force":0.13678,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50014,0.03762,0.05158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5952.0,"contact_point_centroid":[0.50086,0.05595,0.09555],"force_p95":0.09046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22254,"mean_force":0.0533,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50102,0.03745,0.09526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1671.0,"contact_point_centroid":[0.54242,0.05779,0.17337],"force_p95":0.12539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16867,"mean_force":0.08142,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54334,0.07683,0.17495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2305.0,"contact_point_centroid":[0.54091,0.09215,0.17281],"force_p95":0.10417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15609,"mean_force":0.05982,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54042,0.07369,0.17287]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50306,0.01663,0.21527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3625.0,"contact_point_centroid":[0.5012,0.01844,0.05013],"force_p95":0.10874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13496,"mean_force":0.06042,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.499,0.03753,0.05031]},{"body_a":"world","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50613,0.03613,0.09443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4873.0,"contact_point_centroid":[0.49985,0.05634,0.05068],"force_p95":0.07561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07917,"mean_force":0.04388,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03753,0.05032]}],"total_contact_groups":12},"final_pose_error":0.02916,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62008,0.15511,0.14084],"final_tcp_position":[0.61065,0.15427,0.17057],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.48706,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50746,0.0344,0.12803],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":720.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50711,0.03815,0.05956],"tcp_start":[0.50746,0.0344,0.12803],"tcp_to_object_dist_end":0.03401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03807,0.02519],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21373,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18038,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10298.0,"raw_peak_contact_force":0.22641,"subtask_id":"reach_grasp_height","tcp_end":[0.49897,0.03752,0.05028],"tcp_start":[0.50711,0.03815,0.05956],"tcp_to_object_dist_end":0.0285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.5153,0.0388,0.12169],"object_pos_start":[0.51248,0.03807,0.02519],"object_to_goal_dist_end":0.17615,"object_to_goal_dist_start":0.21373,"object_z_max":0.12134,"peak_contact_force":0.1205,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9920.0,"raw_peak_contact_force":0.28841,"subtask_id":"lift_clearance","tcp_end":[0.50691,0.03768,0.14937],"tcp_start":[0.49897,0.03752,0.05028],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.59695,0.12879,0.18155],"object_pos_start":[0.5153,0.0388,0.12169],"object_to_goal_dist_end":0.06469,"object_to_goal_dist_start":0.17615,"object_z_max":0.18094,"peak_contact_force":0.11544,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3976.0,"raw_peak_contact_force":0.16867,"subtask_id":"transport_above","tcp_end":[0.59077,0.12828,0.21051],"tcp_start":[0.50691,0.03768,0.14937],"tcp_to_object_dist_end":0.02962,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.62008,0.15511,0.14084],"object_pos_start":[0.59695,0.12879,0.18155],"object_to_goal_dist_end":0.01941,"object_to_goal_dist_start":0.06469,"object_z_max":0.18366,"peak_contact_force":0.13816,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2963.0,"raw_peak_contact_force":0.48706,"subtask_id":"reach_goal","tcp_end":[0.61065,0.15427,0.17057],"tcp_start":[0.59077,0.12828,0.21051],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77232,"average_solve_count":448.0,"average_success_count":448.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.13422,"descend_approach.approach_speed":0.04582,"descend_to_grasp.descend_speed":0.02808,"descend_to_grasp.grasp_height":0.02189,"descend_to_place.place_height_offset":0.02029,"descend_to_place.place_speed":0.01227,"lift_object.lift_height":0.18557,"lift_object.lift_speed":0.03388,"transport_to_goal.transport_height":0.11986,"transport_to_goal.transport_speed":0.07605},"optimized_scores":{"best_composite_score":0.33355,"best_fitness_score":0.95355,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1146.0,"contact_point_centroid":[0.56589,0.21193,0.2857],"force_p95":0.18929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47165,"mean_force":0.10821,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56328,0.19345,0.28956]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4797,0.04638,-0.00168],"force_p95":0.27097,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29297,"mean_force":0.12661,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46992,0.04628,0.05476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3714.0,"contact_point_centroid":[0.47145,0.02766,0.11331],"force_p95":0.12727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27996,"mean_force":0.09383,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47272,0.04638,0.11592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4320.0,"contact_point_centroid":[0.47258,0.06483,0.11322],"force_p95":0.11711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26347,"mean_force":0.08393,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47275,0.04638,0.11616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1563.0,"contact_point_centroid":[0.5147,0.0925,0.23829],"force_p95":0.14989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25546,"mean_force":0.10305,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51675,0.11123,0.24086]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04864,-0.00217],"force_p95":0.1729,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22999,"mean_force":0.13489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47193,0.04648,0.05503]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1178.0,"contact_point_centroid":[0.56492,0.1757,0.28627],"force_p95":0.13013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22623,"mean_force":0.09249,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56346,0.19382,0.289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1995.0,"contact_point_centroid":[0.51242,0.12243,0.23173],"force_p95":0.11793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21573,"mean_force":0.08122,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51262,0.10425,0.2349]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.4827,0.04873,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49107,0.01904,0.24264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2722.0,"contact_point_centroid":[0.47098,0.02755,0.05109],"force_p95":0.10479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12598,"mean_force":0.07442,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47085,0.04638,0.0539]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47943,0.04349,0.12259]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3096.0,"contact_point_centroid":[0.47057,0.06516,0.05104],"force_p95":0.0953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09653,"mean_force":0.0681,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47085,0.04638,0.0539]}],"total_contact_groups":12},"final_pose_error":0.02531,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57774,0.21013,0.2312],"final_tcp_position":[0.57138,0.21036,0.26451],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.47165,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48261,0.04024,0.18188],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47857,0.0471,0.06219],"tcp_start":[0.48261,0.04024,0.18188],"tcp_to_object_dist_end":0.03644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48269,0.04718,0.02543],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29136,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16815,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7618.0,"raw_peak_contact_force":0.22999,"subtask_id":"reach_grasp_height","tcp_end":[0.47082,0.04637,0.05386],"tcp_start":[0.47857,0.0471,0.06219],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.48205,0.04703,0.15475],"object_pos_start":[0.48269,0.04718,0.02543],"object_to_goal_dist_end":0.22081,"object_to_goal_dist_start":0.29136,"object_z_max":0.15438,"peak_contact_force":0.1316,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8122.0,"raw_peak_contact_force":0.29297,"subtask_id":"lift_clearance","tcp_end":[0.47818,0.04675,0.18679],"tcp_start":[0.47082,0.04637,0.05386],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.56219,0.18298,0.27031],"object_pos_start":[0.48205,0.04703,0.15475],"object_to_goal_dist_end":0.06386,"object_to_goal_dist_start":0.22081,"object_z_max":0.2695,"peak_contact_force":0.11537,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3558.0,"raw_peak_contact_force":0.25546,"subtask_id":"transport_above","tcp_end":[0.559,0.1832,0.30277],"tcp_start":[0.47818,0.04675,0.18679],"tcp_to_object_dist_end":0.03262,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.57774,0.21013,0.2312],"object_pos_start":[0.56219,0.18298,0.27031],"object_to_goal_dist_end":0.01919,"object_to_goal_dist_start":0.06386,"object_z_max":0.27278,"peak_contact_force":0.1338,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2324.0,"raw_peak_contact_force":0.47165,"subtask_id":"reach_goal","tcp_end":[0.57138,0.21036,0.26451],"tcp_start":[0.559,0.1832,0.30277],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.71397,"average_solve_count":458.0,"average_success_count":458.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.13234,"descend_approach.approach_speed":0.034,"descend_to_grasp.descend_speed":0.04144,"descend_to_grasp.grasp_height":0.02269,"descend_to_place.place_height_offset":0.01083,"descend_to_place.place_speed":0.00794,"lift_object.lift_height":0.16557,"lift_object.lift_speed":0.04368,"transport_to_goal.transport_height":0.13948,"transport_to_goal.transport_speed":0.02795},"optimized_scores":{"best_composite_score":0.33473,"best_fitness_score":0.95473,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1089.0,"contact_point_centroid":[0.60289,0.20794,0.27532],"force_p95":0.18478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48884,"mean_force":0.11438,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59914,0.18947,0.27901]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.53394,-0.02039,-0.0016],"force_p95":0.28621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30026,"mean_force":0.12102,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52187,-0.02052,0.05291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3866.0,"contact_point_centroid":[0.52597,-0.00189,0.10157],"force_p95":0.11936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27871,"mean_force":0.08698,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52515,-0.02056,0.10372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4181.0,"contact_point_centroid":[0.5255,-0.03913,0.10203],"force_p95":0.1164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26605,"mean_force":0.08191,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5252,-0.02056,0.10445]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.60179,0.17062,0.27773],"force_p95":0.1304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23084,"mean_force":0.09381,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59895,0.18866,0.28087]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02126,-0.00209],"force_p95":0.14546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18488,"mean_force":0.12944,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52396,-0.02056,0.0534]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.56061,0.08539,0.22222],"force_p95":0.12147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16041,"mean_force":0.08797,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56022,0.06677,0.22534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2877.0,"contact_point_centroid":[0.56068,0.05151,0.22533],"force_p95":0.10818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15873,"mean_force":0.07268,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56132,0.07006,0.22759]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51239,-0.00835,0.24153]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52813,-0.01913,0.12087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3330.0,"contact_point_centroid":[0.52502,-0.00174,0.0506],"force_p95":0.09751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1172,"mean_force":0.0628,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52278,-0.02054,0.05201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3836.0,"contact_point_centroid":[0.52395,-0.03936,0.05072],"force_p95":0.09151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09337,"mean_force":0.05583,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52278,-0.02054,0.05202]}],"total_contact_groups":12},"final_pose_error":0.02992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61089,0.20783,0.20753],"final_tcp_position":[0.60377,0.20875,0.24041],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.48884,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52764,-0.01767,0.1794],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1160.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53118,-0.02068,0.06214],"tcp_start":[0.52764,-0.01767,0.1794],"tcp_to_object_dist_end":0.0366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02076,0.02558],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31655,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14542,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8966.0,"raw_peak_contact_force":0.18488,"subtask_id":"reach_grasp_height","tcp_end":[0.52275,-0.02054,0.05198],"tcp_start":[0.53118,-0.02068,0.06214],"tcp_to_object_dist_end":0.02997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.53778,-0.02075,0.13618],"object_pos_start":[0.53694,-0.02076,0.02558],"object_to_goal_dist_end":0.26849,"object_to_goal_dist_start":0.31655,"object_z_max":0.13583,"peak_contact_force":0.10882,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8132.0,"raw_peak_contact_force":0.30026,"subtask_id":"lift_clearance","tcp_end":[0.53158,-0.02065,0.1669],"tcp_start":[0.52275,-0.02054,0.05198],"tcp_to_object_dist_end":0.03134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.60196,0.17535,0.27024],"object_pos_start":[0.53778,-0.02075,0.13618],"object_to_goal_dist_end":0.08224,"object_to_goal_dist_start":0.26849,"object_z_max":0.2695,"peak_contact_force":0.12412,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5165.0,"raw_peak_contact_force":0.16041,"subtask_id":"transport_above","tcp_end":[0.59677,0.17619,0.30182],"tcp_start":[0.53158,-0.02065,0.1669],"tcp_to_object_dist_end":0.03201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.61089,0.20783,0.20753],"object_pos_start":[0.60196,0.17535,0.27024],"object_to_goal_dist_end":0.01993,"object_to_goal_dist_start":0.08224,"object_z_max":0.27223,"peak_contact_force":0.13154,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2309.0,"raw_peak_contact_force":0.48884,"subtask_id":"reach_goal","tcp_end":[0.60377,0.20875,0.24041],"tcp_start":[0.59677,0.17619,0.30182],"tcp_to_object_dist_end":0.03365,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```