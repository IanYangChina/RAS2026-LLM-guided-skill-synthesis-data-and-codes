## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2105 | 0.54 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5451 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2138 | 0.77 | ❌ rejected |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

## Current Skill (Q=0.210) — your mutation base

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

- **Composite score**: 0.210
- **task_score** (E): 0.538
- **fitness_score**: 0.730  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1554 |
| descend_grasp | 1.00 | 1.00 | 0.0945 |
| grasp | 1.00 | 1.00 | 0.0124 |
| lift | 1.00 | 1.00 | 0.1215 |
| transport | 0.33 | 1.00 | 0.2194 |
| descend_place | 1.00 | 1.00 | 0.0968 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.020, 0.150) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.505, 0.020, 0.150)→(0.506, 0.022, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.056)→(0.497, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 40.333 | 0.149 | 0.186 |
| lift | lift | 1.00 / step_budget | (0.497, 0.021, 0.047)→(0.506, 0.022, 0.168) | (0.511, 0.022, 0.026)→(0.513, 0.023, 0.141) | 0.274→0.222 | 1.00 / 31.333 | 0.098 | 0.436 |
| transport | approach | 0.33 / step_budget | (0.506, 0.022, 0.168)→(0.586, 0.176, 0.294) | (0.513, 0.023, 0.141)→(0.572, 0.167, 0.107) | 0.222→0.150 | 1.00 / 16.667 | 94251.721 | 1.414 |
| descend_place | descend | 1.00 / step_budget | (0.586, 0.176, 0.294)→(0.600, 0.203, 0.203) | (0.572, 0.167, 0.107)→(0.575, 0.178, 0.078) | 0.150→0.128 | 1.00 / 16.333 | 91001.571 | 0.151 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.100
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.613
- phase_breakdown.place_goal_score: 0.687
- phase_breakdown.approach_goal_score: 0.392
- phase_breakdown.grasp_reach_score: 0.642
- phase_breakdown.lift_clear_score: 0.807
- phase_breakdown.approach_object_score: 0.536
- grasp_place_fitness: 0.966

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.966
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.132
- **K-run variance**: 0.0289
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02542,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12448,"approach_object.approach_tolerance":0.02434,"descend_grasp.descend_tolerance":0.00574,"descend_place.place_descent_z":-0.00094,"descend_place.place_tolerance":0.01641,"lift.lift_height":0.14597,"transport.transport_overhead":0.12524,"transport.transport_speed":0.21062},"optimized_scores":{"best_composite_score":0.13225,"best_fitness_score":0.65225,"best_task_score":0.38646},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":697.0,"contact_point_centroid":[0.56737,0.16817,-0.00347],"force_p95":0.77718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75644,"mean_force":0.19709,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59468,0.13841,0.23487]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50997,0.03734,-0.00122],"force_p95":0.25471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40953,"mean_force":0.06204,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49784,0.03803,0.0506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7675.0,"contact_point_centroid":[0.54201,0.06016,0.18301],"force_p95":0.13403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40866,"mean_force":0.08813,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54087,0.07862,0.18672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8346.0,"contact_point_centroid":[0.539,0.09726,0.18453],"force_p95":0.1159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30596,"mean_force":0.08219,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54128,0.079,0.18711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12710.0,"contact_point_centroid":[0.50147,0.05693,0.10247],"force_p95":0.08601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28986,"mean_force":0.05585,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50131,0.03814,0.10157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10694.0,"contact_point_centroid":[0.50247,0.01918,0.09698],"force_p95":0.11044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28517,"mean_force":0.06706,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50091,0.03812,0.09809]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03968,-0.00212],"force_p95":0.15752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20529,"mean_force":0.1317,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50021,0.03824,0.0501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4132.0,"contact_point_centroid":[0.49991,0.01906,0.04841],"force_p95":0.08897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18077,"mean_force":0.05209,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03814,0.04875]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.51251,0.03972,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50306,0.01581,0.22787]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.56691,0.16871,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1227,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61016,0.15662,0.20017]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50573,0.03582,0.10245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4703.0,"contact_point_centroid":[0.49912,0.0573,0.05008],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08078,"mean_force":0.04641,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03814,0.04875]},{"body_a":"left_finger","body_b":"right_finger","contact_count":558.0,"contact_point_centroid":[0.59677,0.14075,0.23921],"force_p95":0.01302,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.0107,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59692,0.14089,0.23688]},{"body_a":"left_finger","body_b":"right_finger","contact_count":835.0,"contact_point_centroid":[0.60967,0.15624,0.20326],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01026,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61002,0.15646,0.20089]}],"total_contact_groups":14},"final_pose_error":0.016,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56691,0.16871,0.01602],"final_tcp_position":[0.61904,0.16654,0.15623],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.48702,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":988.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50734,0.03291,0.15259],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50723,0.03879,0.05804],"tcp_start":[0.50734,0.03291,0.15259],"tcp_to_object_dist_end":0.03246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51255,0.03884,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21301,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15593,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10635.0,"raw_peak_contact_force":0.20529,"subtask_id":"grasp_reach","tcp_end":[0.49898,0.03814,0.04872],"tcp_start":[0.50723,0.03879,0.05804],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.51384,0.0402,0.1294],"object_pos_start":[0.51255,0.03884,0.02555],"object_to_goal_dist_end":0.17518,"object_to_goal_dist_start":0.21301,"object_z_max":0.12929,"peak_contact_force":0.10783,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23548.0,"raw_peak_contact_force":0.40953,"subtask_id":"lift_clear","tcp_end":[0.50796,0.0385,0.15915],"tcp_start":[0.49898,0.03814,0.04872],"tcp_to_object_dist_end":0.03037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5669,0.1687,0.01602],"object_pos_start":[0.51384,0.0402,0.1294],"object_to_goal_dist_end":0.14261,"object_to_goal_dist_start":0.17518,"object_z_max":0.18079,"peak_contact_force":9748.93114,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17276.0,"raw_peak_contact_force":1.75644,"subtask_id":"approach_goal","tcp_end":[0.6033,0.14798,0.24261],"tcp_start":[0.50796,0.0385,0.15915],"tcp_to_object_dist_end":0.23043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.56691,0.16871,0.01602],"object_pos_start":[0.5669,0.1687,0.01602],"object_to_goal_dist_end":0.14261,"object_to_goal_dist_start":0.14261,"object_z_max":0.01602,"peak_contact_force":273004.48702,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1603.0,"raw_peak_contact_force":0.1227,"subtask_id":"place_goal","tcp_end":[0.61904,0.16654,0.15623],"tcp_start":[0.6033,0.14798,0.24261],"tcp_to_object_dist_end":0.14961,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27619,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.20175,"approach_object.approach_tolerance":0.01041,"descend_grasp.descend_tolerance":0.0051,"descend_place.place_descent_z":0.00566,"descend_place.place_tolerance":0.00511,"lift.lift_height":0.14067,"transport.transport_overhead":0.15014,"transport.transport_speed":0.31165},"optimized_scores":{"best_composite_score":0.05278,"best_fitness_score":0.57278,"best_task_score":0.22639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.55078,0.14597,-0.00365],"force_p95":0.76076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22559,"mean_force":0.19125,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55311,0.18148,0.31532]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.48058,0.04633,-0.0012],"force_p95":0.25009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41254,"mean_force":0.05455,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46865,0.04702,0.05058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7721.0,"contact_point_centroid":[0.49935,0.10962,0.20158],"force_p95":0.15273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39278,"mean_force":0.08823,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5005,0.09098,0.20413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12353.0,"contact_point_centroid":[0.47183,0.0659,0.10056],"force_p95":0.08532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29263,"mean_force":0.0555,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47192,0.04708,0.09942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10310.0,"contact_point_centroid":[0.47379,0.02816,0.09555],"force_p95":0.10944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28002,"mean_force":0.06703,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47163,0.04707,0.09678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7944.0,"contact_point_centroid":[0.50847,0.0808,0.20916],"force_p95":0.11411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25906,"mean_force":0.08065,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50467,0.09834,0.21304]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04868,-0.00211],"force_p95":0.1568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20198,"mean_force":0.13103,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47097,0.04728,0.04987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3846.0,"contact_point_centroid":[0.47148,0.02808,0.04783],"force_p95":0.09602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14056,"mean_force":0.05582,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4698,0.04717,0.04865]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48942,0.02167,0.21947]},{"body_a":"world","body_b":"grasp_target","contact_count":3576.0,"contact_point_centroid":[0.55081,0.1459,-0.00199],"force_p95":0.12268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1249,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5707,0.21399,0.26973]},{"body_a":"world","body_b":"grasp_target","contact_count":1812.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47752,0.04606,0.09522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4916.0,"contact_point_centroid":[0.47026,0.06625,0.05108],"force_p95":0.08123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08431,"mean_force":0.04413,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4698,0.04717,0.04865]},{"body_a":"left_finger","body_b":"right_finger","contact_count":648.0,"contact_point_centroid":[0.55472,0.18439,0.32139],"force_p95":0.01347,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.0108,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5549,0.18454,0.31909]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3853.0,"contact_point_centroid":[0.5705,0.21372,0.2722],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57068,0.21394,0.26987]}],"total_contact_groups":14},"final_pose_error":0.00685,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55081,0.1459,0.02602],"final_tcp_position":[0.57817,0.22676,0.23077],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.14869,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.4803,0.04432,0.13896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1812.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47776,0.04794,0.05702],"tcp_start":[0.4803,0.04432,0.13896],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48275,0.04782,0.02557],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29084,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15695,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10562.0,"raw_peak_contact_force":0.20198,"subtask_id":"grasp_reach","tcp_end":[0.46977,0.04716,0.04861],"tcp_start":[0.47776,0.04794,0.05702],"tcp_to_object_dist_end":0.02645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48452,0.04912,0.12516],"object_pos_start":[0.48275,0.04782,0.02557],"object_to_goal_dist_end":0.22995,"object_to_goal_dist_start":0.29084,"object_z_max":0.12505,"peak_contact_force":0.1114,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22804.0,"raw_peak_contact_force":0.41254,"subtask_id":"lift_clear","tcp_end":[0.47821,0.04741,0.15441],"tcp_start":[0.46977,0.04716,0.04861],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55081,0.14586,0.02602],"object_pos_start":[0.48452,0.04912,0.12516],"object_to_goal_dist_end":0.22284,"object_to_goal_dist_start":0.22995,"object_z_max":0.23957,"peak_contact_force":273006.14869,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17075.0,"raw_peak_contact_force":2.22559,"subtask_id":"approach_goal","tcp_end":[0.56141,0.1958,0.33295],"tcp_start":[0.47821,0.04741,0.15441],"tcp_to_object_dist_end":0.31114,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.55081,0.1459,0.02602],"object_pos_start":[0.55081,0.14586,0.02602],"object_to_goal_dist_end":0.22283,"object_to_goal_dist_start":0.22284,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7429.0,"raw_peak_contact_force":0.1249,"subtask_id":"place_goal","tcp_end":[0.57817,0.22676,0.23077],"tcp_start":[0.56141,0.1958,0.33295],"tcp_to_object_dist_end":0.22184,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2623,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.15339,"approach_object.approach_tolerance":0.03163,"descend_grasp.descend_tolerance":0.00503,"descend_place.place_descent_z":-0.00059,"descend_place.place_tolerance":0.01947,"lift.lift_height":0.1767,"transport.transport_overhead":0.13418,"transport.transport_speed":0.31447},"optimized_scores":{"best_composite_score":0.44636,"best_fitness_score":0.96636,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.53429,-0.02097,-0.00112],"force_p95":0.32049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48688,"mean_force":0.07573,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52195,-0.02099,0.04435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19700.0,"contact_point_centroid":[0.5269,-0.00211,0.11641],"force_p95":0.07382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31425,"mean_force":0.04887,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52572,-0.02115,0.11445]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17099.0,"contact_point_centroid":[0.52588,-0.04033,0.11789],"force_p95":0.0793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30722,"mean_force":0.05494,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52576,-0.02115,0.11499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18910.0,"contact_point_centroid":[0.56452,0.06304,0.24684],"force_p95":0.07577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26042,"mean_force":0.05284,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56228,0.08207,0.24635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20138.0,"contact_point_centroid":[0.55977,0.09975,0.2469],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23885,"mean_force":0.04933,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56194,0.08096,0.2457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2611.0,"contact_point_centroid":[0.59328,0.21671,0.26773],"force_p95":0.12689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20429,"mean_force":0.07074,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59848,0.19839,0.26727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3231.0,"contact_point_centroid":[0.60346,0.18103,0.26311],"force_p95":0.1256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1974,"mean_force":0.06058,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59866,0.19906,0.26539]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02143,-0.00204],"force_p95":0.13399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15218,"mean_force":0.12574,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5245,-0.02102,0.04415]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.53702,-0.02132,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51297,-0.00806,0.2318]},{"body_a":"world","body_b":"grasp_target","contact_count":3844.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52829,-0.01938,0.09434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.52401,-0.00192,0.04471],"force_p95":0.06845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09739,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52324,-0.021,0.04268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.52249,-0.04026,0.04565],"force_p95":0.08057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08662,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52325,-0.021,0.04268]}],"total_contact_groups":12},"final_pose_error":0.01922,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.606,0.21996,0.19176],"final_tcp_position":[0.60412,0.21685,0.22138],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.48688,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52716,-0.01691,0.15922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3844.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.53163,-0.02113,0.05256],"tcp_start":[0.52716,-0.01691,0.15922],"tcp_to_object_dist_end":0.02708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02146,0.02585],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31695,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13406,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11283.0,"raw_peak_contact_force":0.15218,"subtask_id":"grasp_reach","tcp_end":[0.52321,-0.021,0.04264],"tcp_start":[0.53163,-0.02113,0.05256],"tcp_to_object_dist_end":0.02168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.54104,-0.0218,0.16709],"object_pos_start":[0.53692,-0.02146,0.02585],"object_to_goal_dist_end":0.26211,"object_to_goal_dist_start":0.31695,"object_z_max":0.16698,"peak_contact_force":0.07466,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36944.0,"raw_peak_contact_force":0.48688,"subtask_id":"lift_clear","tcp_end":[0.53272,-0.02137,0.18979],"tcp_start":[0.52321,-0.021,0.04264],"tcp_to_object_dist_end":0.02418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59754,0.18569,0.27875],"object_pos_start":[0.54104,-0.0218,0.16709],"object_to_goal_dist_end":0.0838,"object_to_goal_dist_start":0.26211,"object_z_max":0.27869,"peak_contact_force":0.08273,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39048.0,"raw_peak_contact_force":0.26042,"subtask_id":"approach_goal","tcp_end":[0.59446,0.18363,0.30713],"tcp_start":[0.53272,-0.02137,0.18979],"tcp_to_object_dist_end":0.02862,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.606,0.21996,0.19176],"object_pos_start":[0.59754,0.18569,0.27875],"object_to_goal_dist_end":0.01801,"object_to_goal_dist_start":0.0838,"object_z_max":0.27875,"peak_contact_force":0.10479,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5842.0,"raw_peak_contact_force":0.20429,"subtask_id":"place_goal","tcp_end":[0.60412,0.21685,0.22138],"tcp_start":[0.59446,0.18363,0.30713],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```