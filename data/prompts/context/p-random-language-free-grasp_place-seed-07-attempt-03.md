## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5718 | 0.95 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1885 | 0.31 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.572) — your mutation base

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
    - 0.05
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    place_descent_z:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.05
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - place_descent_z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.572
- **task_score** (E): 0.954
- **fitness_score**: 0.942  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1682 |
| descend_grasp | 1.00 | 1.00 | 0.0848 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 1.00 | 1.00 | 0.1335 |
| transport | 1.00 | 1.00 | 0.2120 |
| descend_place | 1.00 | 0.33 | 0.0243 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.053) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.053)→(0.497, 0.022, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 45.667 | 0.147 | 0.184 |
| lift | lift | 1.00 / step_budget | (0.497, 0.022, 0.044)→(0.506, 0.022, 0.177) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.153) | 0.273→0.222 | 1.00 / 37.667 | 0.081 | 0.472 |
| transport | approach | 1.00 / step_budget | (0.506, 0.022, 0.177)→(0.593, 0.187, 0.268) | (0.514, 0.022, 0.153)→(0.595, 0.189, 0.238) | 0.222→0.052 | 1.00 / 30.000 | 0.101 | 0.311 |
| descend_place | descend | 1.00 / step_budget | (0.593, 0.187, 0.268)→(0.602, 0.206, 0.260) | (0.595, 0.189, 0.238)→(0.596, 0.215, 0.204) | 0.052→0.019 | 0.33 / 12.667 | 0.026 | 0.307 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.153
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.568
- phase_breakdown.place_goal_score: 0.408
- phase_breakdown.approach_goal_score: 0.365
- phase_breakdown.grasp_reach_score: 0.639
- phase_breakdown.lift_clear_score: 0.607
- phase_breakdown.approach_object_score: 0.821
- grasp_place_fitness: 0.967

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.967
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.593
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91379,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.18574,"descend_place.place_descent_z":0.05354,"lift.lift_height":0.21354,"transport.transport_overhead":0.10772,"transport.transport_speed":0.31511},"optimized_scores":{"best_composite_score":0.52565,"best_fitness_score":0.89565,"best_task_score":0.8605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50999,0.03786,-0.0012],"force_p95":0.27555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48908,"mean_force":0.06835,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49783,0.03843,0.04539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4303.0,"contact_point_centroid":[0.62149,0.14809,0.23308],"force_p95":0.16293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35499,"mean_force":0.09887,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61894,0.16638,0.23764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5487.0,"contact_point_centroid":[0.61446,0.18416,0.23515],"force_p95":0.12018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32752,"mean_force":0.0783,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.619,0.16644,0.23763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16827.0,"contact_point_centroid":[0.55659,0.0762,0.21779],"force_p95":0.10223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31934,"mean_force":0.05984,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55533,0.09537,0.218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19513.0,"contact_point_centroid":[0.50064,0.0577,0.12404],"force_p95":0.07531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30587,"mean_force":0.05213,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50082,0.03853,0.12097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21223.0,"contact_point_centroid":[0.50222,0.01943,0.12014],"force_p95":0.07718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29705,"mean_force":0.04875,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50062,0.03851,0.11838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19017.0,"contact_point_centroid":[0.55428,0.1166,0.21968],"force_p95":0.07533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28228,"mean_force":0.05171,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55776,0.09806,0.2189]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0398,-0.00211],"force_p95":0.15341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20063,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03866,0.0449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50049,0.01931,0.04579],"force_p95":0.06867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16813,"mean_force":0.04016,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03855,0.04354]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50281,0.01781,0.21859]},{"body_a":"world","body_b":"grasp_target","contact_count":2720.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50611,0.03794,0.08525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5154.0,"contact_point_centroid":[0.49819,0.05778,0.04806],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07557,"mean_force":0.04278,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04354]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61232,0.18834,0.15002],"final_tcp_position":[0.62362,0.17086,0.23954],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.48908,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50754,0.03626,0.13786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2720.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50736,0.03922,0.05269],"tcp_start":[0.50754,0.03626,0.13786],"tcp_to_object_dist_end":0.02716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03926,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15278,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12505.0,"raw_peak_contact_force":0.20063,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.03855,0.04351],"tcp_start":[0.50736,0.03922,0.05269],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51447,0.03962,0.17923],"object_pos_start":[0.51251,0.03926,0.0256],"object_to_goal_dist_end":0.17783,"object_to_goal_dist_start":0.21274,"object_z_max":0.17904,"peak_contact_force":0.08245,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40881.0,"raw_peak_contact_force":0.48908,"subtask_id":"lift_clear","tcp_end":[0.50695,0.03886,0.20352],"tcp_start":[0.49917,0.03855,0.04351],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61381,0.16147,0.2095],"object_pos_start":[0.51447,0.03962,0.17923],"object_to_goal_dist_end":0.06684,"object_to_goal_dist_start":0.17783,"object_z_max":0.20948,"peak_contact_force":0.11363,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35844.0,"raw_peak_contact_force":0.31934,"subtask_id":"approach_goal","tcp_end":[0.61357,0.15965,0.24003],"tcp_start":[0.50695,0.03886,0.20352],"tcp_to_object_dist_end":0.03059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.61232,0.18834,0.15002],"object_pos_start":[0.61381,0.16147,0.2095],"object_to_goal_dist_end":0.02254,"object_to_goal_dist_start":0.06684,"object_z_max":0.2095,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9790.0,"raw_peak_contact_force":0.35499,"subtask_id":"place_goal","tcp_end":[0.62362,0.17086,0.23954],"tcp_start":[0.61357,0.15965,0.24003],"tcp_to_object_dist_end":0.0919,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3125,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.02225,"descend_place.place_descent_z":0.01625,"lift.lift_height":0.15867,"transport.transport_overhead":0.08654,"transport.transport_speed":0.35716},"optimized_scores":{"best_composite_score":0.59297,"best_fitness_score":0.96297,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.4803,0.04656,-0.0012],"force_p95":0.26302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44425,"mean_force":0.05989,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4686,0.04717,0.04775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2654.0,"contact_point_centroid":[0.56442,0.23241,0.28533],"force_p95":0.12969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3752,"mean_force":0.08493,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57208,0.21599,0.28842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15803.0,"contact_point_centroid":[0.51846,0.09869,0.22129],"force_p95":0.10422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36317,"mean_force":0.06385,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51573,0.11749,0.22267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1880.0,"contact_point_centroid":[0.57478,0.19745,0.28376],"force_p95":0.19223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30389,"mean_force":0.1175,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57198,0.21587,0.28835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15502.0,"contact_point_centroid":[0.47166,0.06646,0.10905],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28433,"mean_force":0.05181,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47196,0.0473,0.10663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15826.0,"contact_point_centroid":[0.47384,0.02825,0.10775],"force_p95":0.08253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27527,"mean_force":0.05119,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47197,0.0473,0.10691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17161.0,"contact_point_centroid":[0.51542,0.14152,0.22711],"force_p95":0.08712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27202,"mean_force":0.05782,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.519,0.12314,0.22709]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04878,-0.00212],"force_p95":0.15595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20114,"mean_force":0.1316,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47098,0.04742,0.04706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.47165,0.02812,0.04666],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1595,"mean_force":0.04362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04583]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4892,0.02163,0.21944]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47745,0.04628,0.09192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5151.0,"contact_point_centroid":[0.46885,0.06652,0.04944],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07757,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04583]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56776,0.23399,0.23875],"final_tcp_position":[0.57774,0.22536,0.28833],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.44425,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48016,0.04447,0.1384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47771,0.04808,0.05413],"tcp_start":[0.48016,0.04447,0.1384],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04813,0.02557],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.155,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12047.0,"raw_peak_contact_force":0.20114,"subtask_id":"grasp_reach","tcp_end":[0.46976,0.0473,0.0458],"tcp_start":[0.47771,0.04808,0.05413],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.48635,0.04874,0.14669],"object_pos_start":[0.48274,0.04813,0.02557],"object_to_goal_dist_end":0.22043,"object_to_goal_dist_start":0.29066,"object_z_max":0.14658,"peak_contact_force":0.08152,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31466.0,"raw_peak_contact_force":0.44425,"subtask_id":"lift_clear","tcp_end":[0.47846,0.04773,0.17232],"tcp_start":[0.46976,0.0473,0.0458],"tcp_to_object_dist_end":0.02683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56792,0.20802,0.25874],"object_pos_start":[0.48635,0.04874,0.14669],"object_to_goal_dist_end":0.03778,"object_to_goal_dist_start":0.22043,"object_z_max":0.25857,"peak_contact_force":0.11902,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32964.0,"raw_peak_contact_force":0.36317,"subtask_id":"approach_goal","tcp_end":[0.56707,0.20597,0.29188],"tcp_start":[0.47846,0.04773,0.17232],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.56776,0.23399,0.23875],"object_pos_start":[0.56792,0.20802,0.25874],"object_to_goal_dist_end":0.01714,"object_to_goal_dist_start":0.03778,"object_z_max":0.2588,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4534.0,"raw_peak_contact_force":0.3752,"subtask_id":"place_goal","tcp_end":[0.57774,0.22536,0.28833],"tcp_start":[0.56707,0.20597,0.29188],"tcp_to_object_dist_end":0.05131,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19444,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.1623,"descend_place.place_descent_z":0.00018,"lift.lift_height":0.14234,"transport.transport_overhead":0.09186,"transport.transport_speed":0.44851},"optimized_scores":{"best_composite_score":0.59683,"best_fitness_score":0.96683,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.53426,-0.02099,-0.00111],"force_p95":0.33864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48359,"mean_force":0.075,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52212,-0.02105,0.04399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15151.0,"contact_point_centroid":[0.52651,-0.00215,0.09824],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31045,"mean_force":0.04944,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52551,-0.0212,0.09637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13183.0,"contact_point_centroid":[0.52542,-0.04037,0.09836],"force_p95":0.07928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3036,"mean_force":0.05541,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5254,-0.02119,0.09547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20524.0,"contact_point_centroid":[0.56683,0.06937,0.21352],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25131,"mean_force":0.04895,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56364,0.08827,0.21229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20291.0,"contact_point_centroid":[0.56072,0.10521,0.21295],"force_p95":0.0717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21122,"mean_force":0.04911,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56304,0.08638,0.21123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4087.0,"contact_point_centroid":[0.5943,0.22653,0.26038],"force_p95":0.07695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18995,"mean_force":0.05254,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60113,0.20865,0.25942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4197.0,"contact_point_centroid":[0.60619,0.19009,0.25851],"force_p95":0.07725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16105,"mean_force":0.05062,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60107,0.20846,0.25955]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15068,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52457,-0.02108,0.04379]},{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51392,-0.00966,0.21799]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52959,-0.02054,0.08477]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52405,-0.00198,0.04433],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10082,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4161.0,"contact_point_centroid":[0.52255,-0.04032,0.04527],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.05161,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60877,0.22415,0.22388],"final_tcp_position":[0.60545,0.22155,0.25148],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.48359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53015,-0.01963,0.13689],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.5317,-0.02119,0.0522],"tcp_start":[0.53015,-0.01963,0.13689],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0215,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13351,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11297.0,"raw_peak_contact_force":0.15068,"subtask_id":"grasp_reach","tcp_end":[0.52328,-0.02106,0.04228],"tcp_start":[0.5317,-0.02119,0.0522],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.54145,-0.02197,0.1343],"object_pos_start":[0.53692,-0.0215,0.02586],"object_to_goal_dist_end":0.26916,"object_to_goal_dist_start":0.31698,"object_z_max":0.13418,"peak_contact_force":0.07876,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28479.0,"raw_peak_contact_force":0.48359,"subtask_id":"lift_clear","tcp_end":[0.53224,-0.0214,0.15548],"tcp_start":[0.52328,-0.02106,0.04228],"tcp_to_object_dist_end":0.0231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60229,0.19669,0.246],"object_pos_start":[0.54145,-0.02197,0.1343],"object_to_goal_dist_end":0.05019,"object_to_goal_dist_start":0.26916,"object_z_max":0.24594,"peak_contact_force":0.071,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40815.0,"raw_peak_contact_force":0.25131,"subtask_id":"approach_goal","tcp_end":[0.59737,0.19413,0.27224],"tcp_start":[0.53224,-0.0214,0.15548],"tcp_to_object_dist_end":0.02681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.60877,0.22415,0.22388],"object_pos_start":[0.60229,0.19669,0.246],"object_to_goal_dist_end":0.01693,"object_to_goal_dist_start":0.05019,"object_z_max":0.246,"peak_contact_force":0.07852,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8284.0,"raw_peak_contact_force":0.18995,"subtask_id":"place_goal","tcp_end":[0.60545,0.22155,0.25148],"tcp_start":[0.59737,0.19413,0.27224],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```