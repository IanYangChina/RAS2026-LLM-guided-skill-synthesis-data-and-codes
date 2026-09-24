## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1885 | 0.31 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ✅ accepted |

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
| lift | 1.00 | 1.00 | 0.1342 |
| transport | 0.33 | 1.00 | 0.1875 |
| descend_place | 1.00 | 1.00 | 0.0555 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 7.112 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.053) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.053)→(0.497, 0.022, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 45.667 | 0.147 | 0.184 |
| lift | lift | 1.00 / step_budget | (0.497, 0.022, 0.044)→(0.506, 0.022, 0.178) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.154) | 0.273→0.222 | 1.00 / 37.667 | 0.080 | 0.472 |
| transport | approach | 0.33 / step_budget | (0.506, 0.022, 0.178)→(0.583, 0.160, 0.258) | (0.514, 0.022, 0.154)→(0.585, 0.162, 0.228) | 0.222→0.069 | 1.00 / 30.000 | 0.100 | 0.280 |
| descend_place | descend | 1.00 / step_budget | (0.583, 0.160, 0.258)→(0.600, 0.203, 0.243) | (0.585, 0.162, 0.228)→(0.598, 0.204, 0.209) | 0.069→0.019 | 1.00 / 24.333 | 0.138 | 0.256 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.126
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.473
- phase_breakdown.place_goal_score: 0.381
- phase_breakdown.approach_goal_score: 0.095
- phase_breakdown.grasp_reach_score: 0.639
- phase_breakdown.lift_clear_score: 0.428
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
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16204,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.01098,"descend_place.place_descent_z":0.00484,"lift.lift_height":0.21558,"transport.transport_overhead":0.07071,"transport.transport_speed":0.37805},"optimized_scores":{"best_composite_score":0.59541,"best_fitness_score":0.96541,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50982,0.03798,-0.00119],"force_p95":0.27693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48989,"mean_force":0.06787,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49783,0.03843,0.0454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16664.0,"contact_point_centroid":[0.55736,0.07717,0.20295],"force_p95":0.10544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3318,"mean_force":0.06059,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55608,0.09632,0.20327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19472.0,"contact_point_centroid":[0.50072,0.0577,0.12496],"force_p95":0.07546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30629,"mean_force":0.05226,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50084,0.03853,0.12196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21165.0,"contact_point_centroid":[0.50226,0.01944,0.12092],"force_p95":0.07756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29751,"mean_force":0.0489,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50063,0.03852,0.1192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18771.0,"contact_point_centroid":[0.555,0.1175,0.20414],"force_p95":0.07752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29422,"mean_force":0.05247,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55843,0.09895,0.20338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1298.0,"contact_point_centroid":[0.61246,0.18226,0.19828],"force_p95":0.10033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25708,"mean_force":0.07043,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61688,0.16424,0.19985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":953.0,"contact_point_centroid":[0.61977,0.14595,0.19528],"force_p95":0.11752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24522,"mean_force":0.09422,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61693,0.1643,0.19977]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0398,-0.00211],"force_p95":0.15339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20062,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03866,0.04489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50049,0.01931,0.04578],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1682,"mean_force":0.04016,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04353]},{"body_a":"world","body_b":"grasp_target","contact_count":2320.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50252,0.01771,0.21882]},{"body_a":"world","body_b":"grasp_target","contact_count":2908.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.03799,0.08435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.49819,0.05778,0.04806],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07633,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04353]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62001,0.17023,0.16318],"final_tcp_position":[0.62036,0.16813,0.19452],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":21.09021,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":21.09021,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2320.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50751,0.0363,0.13767],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2908.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50736,0.03922,0.05267],"tcp_start":[0.50751,0.0363,0.13767],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03926,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15276,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12504.0,"raw_peak_contact_force":0.20062,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.03855,0.04349],"tcp_start":[0.50736,0.03922,0.05267],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5145,0.03962,0.18083],"object_pos_start":[0.51251,0.03926,0.0256],"object_to_goal_dist_end":0.17812,"object_to_goal_dist_start":0.21274,"object_z_max":0.18064,"peak_contact_force":0.08257,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40781.0,"raw_peak_contact_force":0.48989,"subtask_id":"lift_clear","tcp_end":[0.50697,0.03886,0.20525],"tcp_start":[0.49917,0.03855,0.04349],"tcp_to_object_dist_end":0.02556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61348,0.16228,0.17586],"object_pos_start":[0.5145,0.03962,0.18083],"object_to_goal_dist_end":0.03542,"object_to_goal_dist_start":0.17812,"object_z_max":0.18098,"peak_contact_force":0.1135,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35435.0,"raw_peak_contact_force":0.3318,"subtask_id":"approach_goal","tcp_end":[0.61399,0.16052,0.20656],"tcp_start":[0.50697,0.03886,0.20525],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.62001,0.17023,0.16318],"object_pos_start":[0.61348,0.16228,0.17586],"object_to_goal_dist_end":0.01979,"object_to_goal_dist_start":0.03542,"object_z_max":0.17586,"peak_contact_force":0.11408,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2251.0,"raw_peak_contact_force":0.25708,"subtask_id":"place_goal","tcp_end":[0.62036,0.16813,0.19452],"tcp_start":[0.61399,0.16052,0.20656],"tcp_to_object_dist_end":0.03141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1875,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.23558,"descend_place.place_descent_z":1e-05,"lift.lift_height":0.17655,"transport.transport_overhead":0.14528,"transport.transport_speed":0.26007},"optimized_scores":{"best_composite_score":0.59294,"best_fitness_score":0.96294,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.48032,0.04659,-0.0012],"force_p95":0.25919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44552,"mean_force":0.06174,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46856,0.04716,0.04777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15016.0,"contact_point_centroid":[0.51338,0.08888,0.24477],"force_p95":0.10541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33056,"mean_force":0.06633,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51036,0.10754,0.24629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2886.0,"contact_point_centroid":[0.55636,0.21835,0.29871],"force_p95":0.13009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32105,"mean_force":0.0844,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5639,0.20148,0.30209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2261.0,"contact_point_centroid":[0.56641,0.18328,0.2964],"force_p95":0.15653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31505,"mean_force":0.10604,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56414,0.20191,0.30151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17867.0,"contact_point_centroid":[0.47162,0.06645,0.11762],"force_p95":0.07695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28501,"mean_force":0.05165,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47201,0.04731,0.11529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18163.0,"contact_point_centroid":[0.47388,0.02826,0.11631],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27603,"mean_force":0.05124,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47202,0.04731,0.11552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16198.0,"contact_point_centroid":[0.50995,0.13017,0.25028],"force_p95":0.09892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25702,"mean_force":0.06011,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51273,0.11165,0.25043]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04878,-0.00212],"force_p95":0.15601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20119,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47098,0.04742,0.04708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.47166,0.02812,0.04668],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15939,"mean_force":0.04362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04585]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48936,0.02176,0.21913]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47749,0.04626,0.09204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46885,0.06651,0.04945],"force_p95":0.07586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07758,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4698,0.04731,0.04585]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56872,0.22215,0.24198],"final_tcp_position":[0.5754,0.22142,0.27924],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.44552,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48023,0.04445,0.1385],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47771,0.04808,0.05415],"tcp_start":[0.48023,0.04445,0.1385],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04813,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15504,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.20119,"subtask_id":"grasp_reach","tcp_end":[0.46977,0.0473,0.04582],"tcp_start":[0.47771,0.04808,0.05415],"tcp_to_object_dist_end":0.02407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.48592,0.04872,0.16412],"object_pos_start":[0.48274,0.04813,0.02556],"object_to_goal_dist_end":0.21461,"object_to_goal_dist_start":0.29066,"object_z_max":0.164,"peak_contact_force":0.08026,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36170.0,"raw_peak_contact_force":0.44552,"subtask_id":"lift_clear","tcp_end":[0.47869,0.04775,0.19025],"tcp_start":[0.46977,0.0473,0.04582],"tcp_to_object_dist_end":0.02713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55727,0.18719,0.29094],"object_pos_start":[0.48592,0.04872,0.16412],"object_to_goal_dist_end":0.07743,"object_to_goal_dist_start":0.21461,"object_z_max":0.29075,"peak_contact_force":0.11542,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31214.0,"raw_peak_contact_force":0.33056,"subtask_id":"approach_goal","tcp_end":[0.55543,0.18521,0.32454],"tcp_start":[0.47869,0.04775,0.19025],"tcp_to_object_dist_end":0.03371,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.56872,0.22215,0.24198],"object_pos_start":[0.55727,0.18719,0.29094],"object_to_goal_dist_end":0.01871,"object_to_goal_dist_start":0.07743,"object_z_max":0.29101,"peak_contact_force":0.20871,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5147.0,"raw_peak_contact_force":0.32105,"subtask_id":"place_goal","tcp_end":[0.5754,0.22142,0.27924],"tcp_start":[0.55543,0.18521,0.32454],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82482,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06764,"descend_place.place_descent_z":0.00728,"lift.lift_height":0.12482,"transport.transport_overhead":0.10998,"transport.transport_speed":0.23729},"optimized_scores":{"best_composite_score":0.59684,"best_fitness_score":0.96684,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.5341,-0.02112,-0.00111],"force_p95":0.36124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47949,"mean_force":0.07193,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52219,-0.02105,0.04399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12742.0,"contact_point_centroid":[0.5264,-0.00214,0.08981],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30776,"mean_force":0.04927,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52546,-0.0212,0.0879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11119.0,"contact_point_centroid":[0.52533,-0.04037,0.08993],"force_p95":0.07935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3014,"mean_force":0.05507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52534,-0.02119,0.08703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18550.0,"contact_point_centroid":[0.59619,0.16221,0.24444],"force_p95":0.08363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19085,"mean_force":0.05408,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59146,0.18039,0.24645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16477.0,"contact_point_centroid":[0.58614,0.19649,0.24609],"force_p95":0.09265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19047,"mean_force":0.05951,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59065,0.17801,0.24598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18756.0,"contact_point_centroid":[0.55614,0.03925,0.19074],"force_p95":0.0748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17895,"mean_force":0.05258,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55365,0.05825,0.18904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20359.0,"contact_point_centroid":[0.55209,0.07486,0.1896],"force_p95":0.07201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16726,"mean_force":0.04867,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5529,0.05586,0.18736]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15067,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52457,-0.02108,0.04379]},{"body_a":"world","body_b":"grasp_target","contact_count":2276.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5137,-0.00965,0.21794]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52958,-0.02054,0.08473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52405,-0.00198,0.04433],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10083,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4157.0,"contact_point_centroid":[0.52255,-0.04032,0.04526],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.05164,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]}],"total_contact_groups":12},"final_pose_error":0.01439,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60482,0.22091,0.22253],"final_tcp_position":[0.60484,0.21915,0.25453],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.47949,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2276.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53011,-0.01964,0.13678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.5317,-0.02119,0.05219],"tcp_start":[0.53011,-0.01964,0.13678],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0215,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31698,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1335,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11293.0,"raw_peak_contact_force":0.15067,"subtask_id":"grasp_reach","tcp_end":[0.52328,-0.02106,0.04228],"tcp_start":[0.5317,-0.02119,0.05219],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54185,-0.02195,0.11743],"object_pos_start":[0.53692,-0.0215,0.02586],"object_to_goal_dist_end":0.27411,"object_to_goal_dist_start":0.31698,"object_z_max":0.11731,"peak_contact_force":0.07862,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24003.0,"raw_peak_contact_force":0.47949,"subtask_id":"lift_clear","tcp_end":[0.53195,-0.02139,0.13788],"tcp_start":[0.52328,-0.02106,0.04228],"tcp_to_object_dist_end":0.02273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58446,0.1367,0.2178],"object_pos_start":[0.54185,-0.02195,0.11743],"object_to_goal_dist_end":0.09522,"object_to_goal_dist_start":0.27411,"object_z_max":0.21767,"peak_contact_force":0.07136,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39115.0,"raw_peak_contact_force":0.17895,"subtask_id":"approach_goal","tcp_end":[0.57819,0.1344,0.2432],"tcp_start":[0.53195,-0.02139,0.13788],"tcp_to_object_dist_end":0.02627,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60482,0.22091,0.22253],"object_pos_start":[0.58446,0.1367,0.2178],"object_to_goal_dist_end":0.01748,"object_to_goal_dist_start":0.09522,"object_z_max":0.22253,"peak_contact_force":0.09095,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":35027.0,"raw_peak_contact_force":0.19085,"subtask_id":"place_goal","tcp_end":[0.60484,0.21915,0.25453],"tcp_start":[0.57819,0.1344,0.2432],"tcp_to_object_dist_end":0.03205,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```