## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1507 | 0.33 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5718 | 0.95 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1885 | 0.31 | ✅ accepted |

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

## Current Skill (Q=0.595) — your mutation base

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

- **Composite score**: 0.595
- **task_score** (E): 1.000
- **fitness_score**: 0.965  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1683 |
| descend_grasp | 1.00 | 1.00 | 0.0847 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 1.00 | 1.00 | 0.1451 |
| transport | 0.67 | 1.00 | 0.2085 |
| descend_place | 1.00 | 1.00 | 0.0651 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 7.112 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.053) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.053)→(0.497, 0.022, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 45.667 | 0.147 | 0.184 |
| lift | lift | 1.00 / step_budget | (0.497, 0.022, 0.044)→(0.506, 0.022, 0.189) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.165) | 0.273→0.218 | 1.00 / 39.333 | 0.078 | 0.475 |
| transport | approach | 0.67 / step_budget | (0.506, 0.022, 0.189)→(0.587, 0.180, 0.282) | (0.514, 0.022, 0.165)→(0.587, 0.182, 0.252) | 0.218→0.070 | 1.00 / 29.667 | 0.110 | 0.306 |
| descend_place | descend | 1.00 / step_budget | (0.587, 0.180, 0.282)→(0.601, 0.205, 0.228) | (0.587, 0.182, 0.252)→(0.597, 0.208, 0.193) | 0.070→0.010 | 1.00 / 18.000 | 55983.991 | 0.351 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.786
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.577
- phase_breakdown.place_goal_score: 0.541
- phase_breakdown.approach_goal_score: 0.254
- phase_breakdown.grasp_reach_score: 0.639
- phase_breakdown.lift_clear_score: 0.630
- phase_breakdown.approach_object_score: 0.822
- grasp_place_fitness: 0.967

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.967
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.595
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31776,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.02239,"descend_place.place_descent_z":0.03358,"lift.lift_height":0.17672,"transport.transport_overhead":0.16077,"transport.transport_speed":0.18982},"optimized_scores":{"best_composite_score":0.59541,"best_fitness_score":0.96541,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.51001,0.03786,-0.00121],"force_p95":0.2762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48679,"mean_force":0.06579,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49787,0.03843,0.04537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3702.0,"contact_point_centroid":[0.60068,0.16872,0.22595],"force_p95":0.14555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39391,"mean_force":0.08249,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60494,0.15089,0.22835]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2849.0,"contact_point_centroid":[0.60651,0.13188,0.22566],"force_p95":0.17506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37697,"mean_force":0.10298,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60451,0.15041,0.22979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17694.0,"contact_point_centroid":[0.50131,0.05774,0.11738],"force_p95":0.07528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30411,"mean_force":0.05207,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50152,0.03856,0.11418]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19400.0,"contact_point_centroid":[0.5029,0.01946,0.11384],"force_p95":0.07674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29559,"mean_force":0.04835,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50132,0.03855,0.11199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17355.0,"contact_point_centroid":[0.54933,0.06716,0.22498],"force_p95":0.08739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2668,"mean_force":0.05736,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54805,0.08632,0.22501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19253.0,"contact_point_centroid":[0.54714,0.10742,0.22795],"force_p95":0.07464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22732,"mean_force":0.05076,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55026,0.08879,0.22707]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0398,-0.00211],"force_p95":0.15339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20062,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03866,0.04489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50049,0.01931,0.04578],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1682,"mean_force":0.04016,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04353]},{"body_a":"world","body_b":"grasp_target","contact_count":2320.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50252,0.01771,0.21882]},{"body_a":"world","body_b":"grasp_target","contact_count":2908.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.03799,0.08435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.49819,0.05778,0.04806],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07633,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04353]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61242,0.1735,0.14337],"final_tcp_position":[0.61978,0.16726,0.18155],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":21.09021,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2320.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50751,0.0363,0.13767],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2908.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50736,0.03922,0.05267],"tcp_start":[0.50751,0.0363,0.13767],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03926,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15276,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12504.0,"raw_peak_contact_force":0.20062,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.03855,0.04349],"tcp_start":[0.50736,0.03922,0.05267],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":904.0,"n_steps_budget":990.0,"object_pos_end":[0.5166,0.03974,0.16604],"object_pos_start":[0.51251,0.03926,0.0256],"object_to_goal_dist_end":0.17431,"object_to_goal_dist_start":0.21274,"object_z_max":0.16592,"peak_contact_force":0.0787,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37239.0,"raw_peak_contact_force":0.48679,"subtask_id":"lift_clear","tcp_end":[0.50838,0.03894,0.18984],"tcp_start":[0.49917,0.03855,0.04349],"tcp_to_object_dist_end":0.02519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59573,0.13992,0.23909],"object_pos_start":[0.5166,0.03974,0.16604],"object_to_goal_dist_end":0.10452,"object_to_goal_dist_start":0.17431,"object_z_max":0.23903,"peak_contact_force":0.11494,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36608.0,"raw_peak_contact_force":0.2668,"subtask_id":"approach_goal","tcp_end":[0.59509,0.1386,0.26912],"tcp_start":[0.50838,0.03894,0.18984],"tcp_to_object_dist_end":0.03007,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.61242,0.1735,0.14337],"object_pos_start":[0.59573,0.13992,0.23909],"object_to_goal_dist_end":0.01527,"object_to_goal_dist_start":0.10452,"object_z_max":0.23909,"peak_contact_force":167951.73011,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6551.0,"raw_peak_contact_force":0.39391,"subtask_id":"place_goal","tcp_end":[0.61978,0.16726,0.18155],"tcp_start":[0.59509,0.1386,0.26912],"tcp_to_object_dist_end":0.03938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20909,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17494,"descend_place.place_descent_z":0.02762,"lift.lift_height":0.16036,"transport.transport_overhead":0.13308,"transport.transport_speed":0.32226},"optimized_scores":{"best_composite_score":0.59294,"best_fitness_score":0.96294,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.48036,0.04663,-0.0012],"force_p95":0.25664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44336,"mean_force":0.06174,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46857,0.04716,0.04776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16211.0,"contact_point_centroid":[0.51872,0.09829,0.24007],"force_p95":0.1021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3515,"mean_force":0.06227,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51566,0.11702,0.24132]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2135.0,"contact_point_centroid":[0.57356,0.19449,0.29272],"force_p95":0.14001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28873,"mean_force":0.09795,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57044,0.21291,0.29776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16231.0,"contact_point_centroid":[0.47151,0.06645,0.10987],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28405,"mean_force":0.0513,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47193,0.0473,0.10733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17220.0,"contact_point_centroid":[0.515,0.13996,0.2461],"force_p95":0.08757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28401,"mean_force":0.05774,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51824,0.12147,0.24591]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16467.0,"contact_point_centroid":[0.47383,0.02824,0.10868],"force_p95":0.08175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27466,"mean_force":0.05101,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47197,0.0473,0.10781]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2588.0,"contact_point_centroid":[0.56322,0.22946,0.29602],"force_p95":0.12178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23244,"mean_force":0.08023,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5702,0.21247,0.29933]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04878,-0.00212],"force_p95":0.15599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20117,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47098,0.04742,0.04708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.47165,0.02812,0.04667],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15941,"mean_force":0.04362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04584]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48934,0.02173,0.2192]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47747,0.04628,0.09199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46885,0.06652,0.04945],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07758,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04585]}],"total_contact_groups":12},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57272,0.22507,0.22825],"final_tcp_position":[0.57635,0.22321,0.26408],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.44336,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48019,0.04447,0.1384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47771,0.04808,0.05415],"tcp_start":[0.48019,0.04447,0.1384],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04813,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15503,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.20117,"subtask_id":"grasp_reach","tcp_end":[0.46976,0.0473,0.04581],"tcp_start":[0.47771,0.04808,0.05415],"tcp_to_object_dist_end":0.02406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.48622,0.04875,0.14866],"object_pos_start":[0.48274,0.04813,0.02556],"object_to_goal_dist_end":0.21973,"object_to_goal_dist_start":0.29066,"object_z_max":0.14854,"peak_contact_force":0.08104,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32840.0,"raw_peak_contact_force":0.44336,"subtask_id":"lift_clear","tcp_end":[0.47849,0.04773,0.17416],"tcp_start":[0.46976,0.0473,0.04581],"tcp_to_object_dist_end":0.02666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56819,0.20629,0.29759],"object_pos_start":[0.48622,0.04875,0.14866],"object_to_goal_dist_end":0.07211,"object_to_goal_dist_start":0.21973,"object_z_max":0.29751,"peak_contact_force":0.145,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33431.0,"raw_peak_contact_force":0.3515,"subtask_id":"approach_goal","tcp_end":[0.56617,0.20414,0.33099],"tcp_start":[0.47849,0.04773,0.17416],"tcp_to_object_dist_end":0.03353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.57272,0.22507,0.22825],"object_pos_start":[0.56819,0.20629,0.29759],"object_to_goal_dist_end":0.01016,"object_to_goal_dist_start":0.07211,"object_z_max":0.29759,"peak_contact_force":0.13218,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4723.0,"raw_peak_contact_force":0.28873,"subtask_id":"place_goal","tcp_end":[0.57635,0.22321,0.26408],"tcp_start":[0.56617,0.20414,0.33099],"tcp_to_object_dist_end":0.03606,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.395,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03445,"descend_place.place_descent_z":0.03864,"lift.lift_height":0.22231,"transport.transport_overhead":0.05482,"transport.transport_speed":0.28952},"optimized_scores":{"best_composite_score":0.59684,"best_fitness_score":0.96684,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.53394,-0.02098,-0.00111],"force_p95":0.34848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49534,"mean_force":0.07735,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52196,-0.02105,0.04401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5265.0,"contact_point_centroid":[0.59544,0.23067,0.23992],"force_p95":0.09206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37129,"mean_force":0.05994,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60215,0.21282,0.23968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21050.0,"contact_point_centroid":[0.526,-0.00213,0.1225],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31797,"mean_force":0.04901,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52475,-0.02117,0.12056]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18285.0,"contact_point_centroid":[0.52497,-0.04034,0.12385],"force_p95":0.07937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31002,"mean_force":0.05507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52478,-0.02117,0.12099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18781.0,"contact_point_centroid":[0.56485,0.06987,0.2225],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30017,"mean_force":0.05377,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56306,0.08894,0.2222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19899.0,"contact_point_centroid":[0.55883,0.10359,0.22241],"force_p95":0.07297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25705,"mean_force":0.04977,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56176,0.08491,0.22128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5527.0,"contact_point_centroid":[0.60702,0.19495,0.23706],"force_p95":0.08005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22276,"mean_force":0.05681,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60228,0.2132,0.23959]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15067,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52457,-0.02108,0.04379]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51363,-0.00963,0.2181]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52959,-0.02054,0.08472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52405,-0.00198,0.04433],"force_p95":0.06854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10083,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52255,-0.04032,0.04526],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.05164,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60627,0.22642,0.2071],"final_tcp_position":[0.60628,0.2242,0.23762],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.49534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53013,-0.01964,0.13677],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.5317,-0.02119,0.05219],"tcp_start":[0.53013,-0.01964,0.13677],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0215,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1335,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11293.0,"raw_peak_contact_force":0.15067,"subtask_id":"grasp_reach","tcp_end":[0.52328,-0.02106,0.04228],"tcp_start":[0.5317,-0.02119,0.05219],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53859,-0.02175,0.17939],"object_pos_start":[0.53692,-0.0215,0.02586],"object_to_goal_dist_end":0.26112,"object_to_goal_dist_start":0.31698,"object_z_max":0.1792,"peak_contact_force":0.07394,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39478.0,"raw_peak_contact_force":0.49534,"subtask_id":"lift_clear","tcp_end":[0.5307,-0.02134,0.20226],"tcp_start":[0.52328,-0.02106,0.04228],"tcp_to_object_dist_end":0.0242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59845,0.19919,0.21831],"object_pos_start":[0.53859,-0.02175,0.17939],"object_to_goal_dist_end":0.03279,"object_to_goal_dist_start":0.26112,"object_z_max":0.21825,"peak_contact_force":0.0714,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38680.0,"raw_peak_contact_force":0.30017,"subtask_id":"approach_goal","tcp_end":[0.59826,0.19743,0.24707],"tcp_start":[0.5307,-0.02134,0.20226],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.60627,0.22642,0.2071],"object_pos_start":[0.59845,0.19919,0.21831],"object_to_goal_dist_end":0.00427,"object_to_goal_dist_start":0.03279,"object_z_max":0.21831,"peak_contact_force":0.10923,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10792.0,"raw_peak_contact_force":0.37129,"subtask_id":"place_goal","tcp_end":[0.60628,0.2242,0.23762],"tcp_start":[0.59826,0.19743,0.24707],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```