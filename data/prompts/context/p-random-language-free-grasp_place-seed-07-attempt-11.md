## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3541 | 0.62 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2105 | 0.54 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5451 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.354) — your mutation base

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

- **Composite score**: 0.354
- **task_score** (E): 0.618
- **fitness_score**: 0.774  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1681 |
| descend_grasp | 1.00 | 1.00 | 0.0848 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 0.33 | 1.00 | 0.1618 |
| transport | 0.33 | 1.00 | 0.0872 |
| descend_place | 1.00 | 1.00 | 0.1100 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.053) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.053)→(0.497, 0.022, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 45.667 | 0.147 | 0.184 |
| lift | lift | 0.33 / step_budget | (0.497, 0.022, 0.044)→(0.504, 0.022, 0.206) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.181) | 0.273→0.217 | 1.00 / 39.333 | 0.085 | 0.479 |
| transport | approach | 0.33 / step_budget | (0.537, 0.080, 0.252)→(0.577, 0.142, 0.283) | (0.511, 0.022, 0.181)→(0.563, 0.133, 0.148) | 0.217→0.161 | 1.00 / 23.333 | 0.106 | 1.019 |
| descend_place | descend | 1.00 / step_budget | (0.577, 0.142, 0.283)→(0.598, 0.197, 0.213) | (0.565, 0.128, 0.157)→(0.580, 0.181, 0.118) | 0.153→0.093 | 1.00 / 12.000 | 0.161 | 0.301 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.840
- phase_score: 0.650
- phase_breakdown.place_goal_score: 0.743
- phase_breakdown.approach_goal_score: 0.441
- phase_breakdown.grasp_reach_score: 0.654
- phase_breakdown.lift_clear_score: 0.594
- phase_breakdown.approach_object_score: 0.820
- grasp_place_fitness: 0.885

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.885
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.840
- **Median Q (composite search score)**: 0.435
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.385


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19658,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.26521,"descend_place.place_descent_z":0.00859,"lift.lift_height":0.2546,"transport.transport_arc_height":0.16262,"transport.transport_overhead":0.05152,"transport.transport_speed":0.15826},"optimized_scores":{"best_composite_score":0.46517,"best_fitness_score":0.88517,"best_task_score":0.83954},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.50965,0.03782,-0.0012],"force_p95":0.27826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49184,"mean_force":0.07038,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4978,0.03843,0.04539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2321.0,"contact_point_centroid":[0.61091,0.13772,0.18799],"force_p95":0.15496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36432,"mean_force":0.10116,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60911,0.15634,0.19201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2986.0,"contact_point_centroid":[0.60458,0.1743,0.18963],"force_p95":0.13402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3423,"mean_force":0.08028,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60918,0.15643,0.19175]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17939.0,"contact_point_centroid":[0.54877,0.06864,0.23268],"force_p95":0.08384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34095,"mean_force":0.05621,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54743,0.08777,0.23288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19481.0,"contact_point_centroid":[0.49977,0.05765,0.12478],"force_p95":0.07545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30776,"mean_force":0.05227,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4999,0.03848,0.12178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21161.0,"contact_point_centroid":[0.50135,0.01939,0.12078],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29881,"mean_force":0.04893,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49972,0.03847,0.11906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19059.0,"contact_point_centroid":[0.54537,0.10751,0.23402],"force_p95":0.07644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28813,"mean_force":0.0522,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54837,0.0888,0.2333]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0398,-0.00211],"force_p95":0.15341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20063,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03866,0.0449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50049,0.01931,0.04579],"force_p95":0.06867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16813,"mean_force":0.04016,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03855,0.04354]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50281,0.01781,0.21859]},{"body_a":"world","body_b":"grasp_target","contact_count":2720.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50611,0.03794,0.08525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5154.0,"contact_point_centroid":[0.49819,0.05778,0.04806],"force_p95":0.07255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07557,"mean_force":0.04278,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04354]}],"total_contact_groups":12},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61403,0.1685,0.12292],"final_tcp_position":[0.61959,0.16752,0.15654],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.49184,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50754,0.03626,0.13786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2720.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50736,0.03922,0.05269],"tcp_start":[0.50754,0.03626,0.13786],"tcp_to_object_dist_end":0.02716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03926,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15278,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12505.0,"raw_peak_contact_force":0.20063,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.03855,0.04351],"tcp_start":[0.50736,0.03922,0.05269],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51256,0.03952,0.18048],"object_pos_start":[0.51251,0.03926,0.0256],"object_to_goal_dist_end":0.17937,"object_to_goal_dist_start":0.21274,"object_z_max":0.18029,"peak_contact_force":0.08261,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40785.0,"raw_peak_contact_force":0.49184,"subtask_id":"lift_clear","tcp_end":[0.50508,0.03876,0.20492],"tcp_start":[0.49917,0.03855,0.04351],"tcp_to_object_dist_end":0.02557,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6013,0.14925,0.19325],"object_pos_start":[0.51256,0.03952,0.18048],"object_to_goal_dist_end":0.05964,"object_to_goal_dist_start":0.17937,"object_z_max":0.21659,"peak_contact_force":0.09955,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36998.0,"raw_peak_contact_force":0.34095,"subtask_id":"approach_goal","tcp_end":[0.60263,0.148,0.22371],"tcp_start":[0.50508,0.03876,0.20492],"tcp_to_object_dist_end":0.03051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.61403,0.1685,0.12292],"object_pos_start":[0.6013,0.14925,0.19325],"object_to_goal_dist_end":0.02624,"object_to_goal_dist_start":0.05964,"object_z_max":0.19325,"peak_contact_force":0.15675,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5307.0,"raw_peak_contact_force":0.36432,"subtask_id":"place_goal","tcp_end":[0.61959,0.16752,0.15654],"tcp_start":[0.60263,0.148,0.22371],"tcp_to_object_dist_end":0.0341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81928,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.15294,"descend_place.place_descent_z":0.00035,"lift.lift_height":0.23949,"transport.transport_arc_height":0.12523,"transport.transport_overhead":0.07105,"transport.transport_speed":0.1963},"optimized_scores":{"best_composite_score":0.16173,"best_fitness_score":0.58173,"best_task_score":0.23759},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2249.0,"contact_point_centroid":[0.53489,0.18032,-0.00276],"force_p95":0.2306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56621,"mean_force":0.15778,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55626,0.18828,0.35536]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47996,0.04627,-0.0012],"force_p95":0.26915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45074,"mean_force":0.06551,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46848,0.04716,0.04776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9613.0,"contact_point_centroid":[0.4862,0.04365,0.27693],"force_p95":0.14064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4128,"mean_force":0.08569,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48248,0.06177,0.27952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10179.0,"contact_point_centroid":[0.4845,0.08282,0.28087],"force_p95":0.12569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32972,"mean_force":0.0797,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48402,0.06437,0.28299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19499.0,"contact_point_centroid":[0.47062,0.06637,0.12694],"force_p95":0.07816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28736,"mean_force":0.05245,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47089,0.04724,0.12501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19540.0,"contact_point_centroid":[0.47264,0.0282,0.12519],"force_p95":0.08473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27932,"mean_force":0.05297,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47087,0.04723,0.12475]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04878,-0.00212],"force_p95":0.15602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20121,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47098,0.04742,0.04708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.47166,0.02812,0.04668],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15938,"mean_force":0.04362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.0473,0.04585]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48934,0.02164,0.21949]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47749,0.04625,0.09209]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.53509,0.17905,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57668,0.22425,0.29354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46885,0.06651,0.04946],"force_p95":0.07586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07759,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4698,0.0473,0.04586]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2523.0,"contact_point_centroid":[0.5554,0.18734,0.35752],"force_p95":0.01126,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55582,0.18756,0.35524]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1244.0,"contact_point_centroid":[0.57647,0.22401,0.29573],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01031,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57669,0.22426,0.29339]}],"total_contact_groups":14},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53509,0.17905,0.02602],"final_tcp_position":[0.57828,0.22681,0.23975],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.56621,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48024,0.04441,0.13863],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47771,0.04808,0.05416],"tcp_start":[0.48024,0.04441,0.13863],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04813,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15506,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.20121,"subtask_id":"grasp_reach","tcp_end":[0.46977,0.0473,0.04582],"tcp_start":[0.47771,0.04808,0.05416],"tcp_to_object_dist_end":0.02407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48246,0.04855,0.18186],"object_pos_start":[0.48274,0.04813,0.02556],"object_to_goal_dist_end":0.21156,"object_to_goal_dist_start":0.29066,"object_z_max":0.18167,"peak_contact_force":0.09904,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39177.0,"raw_peak_contact_force":0.45074,"subtask_id":"lift_clear","tcp_end":[0.47635,0.04759,0.20928],"tcp_start":[0.46977,0.0473,0.04582],"tcp_to_object_dist_end":0.02811,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1576.0,"n_steps_budget":1000.0,"object_pos_end":[0.53119,0.19174,0.00027],"object_pos_start":[0.48246,0.04855,0.18186],"object_to_goal_dist_end":0.23863,"object_to_goal_dist_start":0.21156,"object_z_max":0.31518,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24564.0,"raw_peak_contact_force":2.56621,"subtask_id":"approach_goal","tcp_end":[0.57632,0.22235,0.34637],"tcp_start":[0.57611,0.22138,0.34848],"tcp_to_object_dist_end":0.35037,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.53509,0.17905,0.02602],"object_pos_start":[0.53509,0.17905,0.02602],"object_to_goal_dist_end":0.21558,"object_to_goal_dist_start":0.21558,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2392.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57828,0.22681,0.23975],"tcp_start":[0.57632,0.22235,0.34637],"tcp_to_object_dist_end":0.22322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03101,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.28634,"descend_place.place_descent_z":0.03686,"lift.lift_height":0.21263,"transport.transport_arc_height":0.06223,"transport.transport_overhead":0.0699,"transport.transport_speed":0.12335},"optimized_scores":{"best_composite_score":0.43528,"best_fitness_score":0.85528,"best_task_score":0.77689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.53394,-0.02098,-0.00111],"force_p95":0.34617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49461,"mean_force":0.07676,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52197,-0.02105,0.04401]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11611.0,"contact_point_centroid":[0.5703,0.14414,0.25657],"force_p95":0.11443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41692,"mean_force":0.08133,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57382,0.12586,0.25835]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13518.0,"contact_point_centroid":[0.57684,0.10807,0.25506],"force_p95":0.1141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32996,"mean_force":0.07204,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57398,0.12637,0.25822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21048.0,"contact_point_centroid":[0.52628,-0.00214,0.12257],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31755,"mean_force":0.049,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52503,-0.02118,0.12063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18283.0,"contact_point_centroid":[0.52525,-0.04035,0.12393],"force_p95":0.07934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30955,"mean_force":0.05506,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52506,-0.02118,0.12106]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15067,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52457,-0.02108,0.04379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18067.0,"contact_point_centroid":[0.54064,-0.00525,0.24513],"force_p95":0.08108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14891,"mean_force":0.05431,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53946,0.01377,0.24436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18701.0,"contact_point_centroid":[0.53991,0.03188,0.24446],"force_p95":0.07882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14244,"mean_force":0.0523,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53916,0.01283,0.2433]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51397,-0.00968,0.21781]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52958,-0.02054,0.08476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52405,-0.00198,0.04433],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10082,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4161.0,"contact_point_centroid":[0.52255,-0.04032,0.04527],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.0516,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]}],"total_contact_groups":12},"final_pose_error":0.03475,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59057,0.19556,0.2047],"final_tcp_position":[0.59704,0.19568,0.24266],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.49461,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53012,-0.01964,0.13687],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.5317,-0.02119,0.0522],"tcp_start":[0.53012,-0.01964,0.13687],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0215,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13351,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11297.0,"raw_peak_contact_force":0.15067,"subtask_id":"grasp_reach","tcp_end":[0.52328,-0.02106,0.04228],"tcp_start":[0.5317,-0.02119,0.0522],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53916,-0.02177,0.17949],"object_pos_start":[0.53692,-0.0215,0.02586],"object_to_goal_dist_end":0.26097,"object_to_goal_dist_start":0.31697,"object_z_max":0.1793,"peak_contact_force":0.07393,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39474.0,"raw_peak_contact_force":0.49461,"subtask_id":"lift_clear","tcp_end":[0.53125,-0.02136,0.20236],"tcp_start":[0.52328,-0.02106,0.04228],"tcp_to_object_dist_end":0.0242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5573,0.05664,0.25193],"object_pos_start":[0.53916,-0.02177,0.17949],"object_to_goal_dist_end":0.18458,"object_to_goal_dist_start":0.26097,"object_z_max":0.2519,"peak_contact_force":0.09592,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36768.0,"raw_peak_contact_force":0.14891,"subtask_id":"approach_goal","tcp_end":[0.553,0.05575,0.27997],"tcp_start":[0.53125,-0.02136,0.20236],"tcp_to_object_dist_end":0.02838,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59057,0.19556,0.2047],"object_pos_start":[0.5573,0.05664,0.25193],"object_to_goal_dist_end":0.03787,"object_to_goal_dist_start":0.18458,"object_z_max":0.25193,"peak_contact_force":0.2024,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":25129.0,"raw_peak_contact_force":0.41692,"subtask_id":"place_goal","tcp_end":[0.59704,0.19568,0.24266],"tcp_start":[0.553,0.05575,0.27997],"tcp_to_object_dist_end":0.03851,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```