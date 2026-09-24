## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → grasp → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | -0.0576 | 0.18 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0907 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3541 | 0.62 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2105 | 0.54 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.058) — your mutation base

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

- **Composite score**: -0.058
- **task_score** (E): 0.181
- **fitness_score**: 0.542  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1682 |
| descend_grasp | 1.00 | 1.00 | 0.0736 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 0.67 | 0.1614 |
| secure_grasp | 1.00 | 1.00 | 0.0000 |
| transport | 0.00 | 1.00 | 0.0001 |
| descend_place | 1.00 | 1.00 | 0.2044 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.505, 0.022, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.022, 0.064)→(0.497, 0.021, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 30.000 | 0.150 | 0.190 |
| lift | lift | 1.00 / step_budget | (0.497, 0.021, 0.055)→(0.507, 0.022, 0.216) | (0.511, 0.022, 0.026)→(0.507, 0.031, 0.163) | 0.274→0.215 | 0.67 / 6.667 | 0.102 | 0.300 |
| secure_grasp | grasp | 1.00 / step_budget | (0.501, 0.021, 0.207)→(0.501, 0.021, 0.207) | (0.507, 0.031, 0.163)→(0.508, 0.056, 0.016) | 0.215→0.258 | 1.00 / 8.000 | 3249.677 | 1.793 |
| transport | approach | 0.00 / guard_failure | (0.501, 0.021, 0.207)→(0.501, 0.021, 0.207) | (0.508, 0.056, 0.016)→(0.508, 0.056, 0.016) | 0.258→0.258 | 1.00 / 8.000 | 0.123 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.501, 0.021, 0.207)→(0.597, 0.196, 0.192) | (0.508, 0.056, 0.016)→(0.508, 0.056, 0.016) | 0.258→0.258 | 1.00 / 8.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.225
- phase_score: 0.458
- phase_breakdown.place_goal_score: 0.729
- phase_breakdown.approach_goal_score: 0.022
- phase_breakdown.grasp_reach_score: 0.070
- phase_breakdown.lift_clear_score: 0.646
- phase_breakdown.approach_object_score: 0.822
- grasp_place_fitness: 0.564

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.564
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.225
- **Median Q (composite search score)**: -0.067
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40513,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12861,"descend_grasp.descend_grasp_speed":0.16474,"descend_place.place_descent_z":0.01461,"descend_place.place_speed":0.0784,"lift.lift_height":0.19511,"lift.lift_speed":0.03612,"transport.transport_arc_height":0.05859,"transport.transport_overhead":0.05035,"transport.transport_speed":0.18505},"optimized_scores":{"best_composite_score":-0.03599,"best_fitness_score":0.56401,"best_task_score":0.22459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1835.0,"contact_point_centroid":[0.51163,0.03073,-0.00256],"force_p95":0.24157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55932,"mean_force":0.14578,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.50249,0.03821,0.19255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.50482,0.05557,0.19594],"force_p95":0.36796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37624,"mean_force":0.19446,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.50818,0.03866,0.20158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6026.0,"contact_point_centroid":[0.50047,0.0568,0.11859],"force_p95":0.14109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26158,"mean_force":0.08995,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50114,0.0382,0.12167]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.50997,0.03813,-0.00152],"force_p95":0.23325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25537,"mean_force":0.08575,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49786,0.03803,0.05564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.50985,0.0229,0.19622],"force_p95":0.14558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2263,"mean_force":0.04383,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.50801,0.03866,0.20131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6357.0,"contact_point_centroid":[0.50166,0.01989,0.11798],"force_p95":0.12872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20901,"mean_force":0.08166,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50113,0.0382,0.12158]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03971,-0.00211],"force_p95":0.15499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20153,"mean_force":0.1309,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50004,0.03822,0.05609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3133.0,"contact_point_centroid":[0.49937,0.01942,0.05134],"force_p95":0.1004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17562,"mean_force":0.06605,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49885,0.03812,0.05475]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50267,0.01774,0.21881]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5061,0.03743,0.10073]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.51162,0.03075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50231,0.0382,0.19227]},{"body_a":"world","body_b":"grasp_target","contact_count":2840.0,"contact_point_centroid":[0.51162,0.03075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56002,0.10315,0.16976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3122.0,"contact_point_centroid":[0.49838,0.05707,0.05241],"force_p95":0.09973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10038,"mean_force":0.06692,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49886,0.03812,0.05475]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1726.0,"contact_point_centroid":[0.50272,0.0382,0.1947],"force_p95":0.01189,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01047,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.50238,0.03821,0.19238]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3033.0,"contact_point_centroid":[0.56025,0.10308,0.17213],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01044,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56001,0.10314,0.16977]},{"body_a":"left_finger","body_b":"right_finger","contact_count":13.0,"contact_point_centroid":[0.50218,0.03816,0.19509],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01087,"mean_force":0.01034,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50231,0.0382,0.19227]}],"total_contact_groups":16},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51162,0.03075,0.01602],"final_tcp_position":[0.61689,0.16421,0.15319],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273005.74497,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50751,0.03629,0.13773],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50711,0.03878,0.06421],"tcp_start":[0.50751,0.03629,0.13773],"tcp_to_object_dist_end":0.03859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51256,0.03899,0.02561],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21288,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15207,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8055.0,"raw_peak_contact_force":0.20153,"subtask_id":"grasp_reach","tcp_end":[0.49882,0.03812,0.05471],"tcp_start":[0.50711,0.03878,0.06421],"tcp_to_object_dist_end":0.03219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.51125,0.0369,0.16374],"object_pos_start":[0.51256,0.03899,0.02561],"object_to_goal_dist_end":0.17965,"object_to_goal_dist_start":0.21288,"object_z_max":0.16359,"peak_contact_force":0.23355,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12478.0,"raw_peak_contact_force":0.26158,"subtask_id":"lift_clear","tcp_end":[0.50807,0.03865,0.2014],"tcp_start":[0.49882,0.03812,0.05471],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51162,0.03075,0.01602],"object_pos_start":[0.51125,0.0369,0.16374],"object_to_goal_dist_end":0.22402,"object_to_goal_dist_start":0.17965,"object_z_max":0.16381,"peak_contact_force":0.12263,"phase_name":"secure_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3777.0,"raw_peak_contact_force":1.55932,"subtask_id":"grasp_reach","tcp_end":[0.50233,0.0382,0.1923],"tcp_start":[0.50233,0.0382,0.1923],"tcp_to_object_dist_end":0.17668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51162,0.03075,0.01602],"object_pos_start":[0.51162,0.03075,0.01602],"object_to_goal_dist_end":0.22402,"object_to_goal_dist_start":0.22402,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.50225,0.0382,0.19216],"tcp_start":[0.50228,0.0382,0.19223],"tcp_to_object_dist_end":0.17655,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.51162,0.03075,0.01602],"object_pos_start":[0.51162,0.03075,0.01602],"object_to_goal_dist_end":0.22402,"object_to_goal_dist_start":0.22402,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5873.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61689,0.16421,0.15319],"tcp_start":[0.50225,0.0382,0.19216],"tcp_to_object_dist_end":0.21842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35023,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.13338,"descend_grasp.descend_grasp_speed":0.13385,"descend_place.place_descent_z":0.00121,"descend_place.place_speed":0.09517,"lift.lift_height":0.20822,"lift.lift_speed":0.01246,"transport.transport_arc_height":0.06531,"transport.transport_overhead":0.05474,"transport.transport_speed":0.26162},"optimized_scores":{"best_composite_score":-0.06951,"best_fitness_score":0.53049,"best_task_score":0.15961},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1975.0,"contact_point_centroid":[0.47731,0.09115,-0.00246],"force_p95":0.19967,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86433,"mean_force":0.14922,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.47349,0.04691,0.20663]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.48005,0.04686,-0.00157],"force_p95":0.2181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25611,"mean_force":0.08532,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46888,0.04672,0.0567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6191.0,"contact_point_centroid":[0.46995,0.06516,0.12247],"force_p95":0.12782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2248,"mean_force":0.08548,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47176,0.04688,0.12601]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04869,-0.00213],"force_p95":0.15942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20707,"mean_force":0.13188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47102,0.04695,0.0571]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5375.0,"contact_point_centroid":[0.4721,0.02834,0.11841],"force_p95":0.13207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19155,"mean_force":0.09101,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4715,0.04686,0.12269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2890.0,"contact_point_centroid":[0.47037,0.02815,0.05175],"force_p95":0.10871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17572,"mean_force":0.07112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46987,0.04684,0.05588]},{"body_a":"world","body_b":"grasp_target","contact_count":1976.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48929,0.02168,0.21934]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47794,0.04591,0.10138]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.47754,0.09143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.47316,0.04688,0.20613]},{"body_a":"world","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.47754,0.09143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52389,0.13605,0.21264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3003.0,"contact_point_centroid":[0.46834,0.0657,0.0526],"force_p95":0.10185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10252,"mean_force":0.06958,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46988,0.04684,0.05589]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1990.0,"contact_point_centroid":[0.47397,0.04693,0.20865],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01062,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.47336,0.0469,0.20644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3633.0,"contact_point_centroid":[0.5242,0.13623,0.21505],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01039,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52404,0.13632,0.21267]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12.0,"contact_point_centroid":[0.47364,0.0469,0.20818],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.01088,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.47316,0.04688,0.20613]}],"total_contact_groups":14},"final_pose_error":0.01486,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47754,0.09143,0.01602],"final_tcp_position":[0.57407,0.21977,0.2229],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273004.12084,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1976.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48022,0.04446,0.13848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":948.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47788,0.0476,0.06447],"tcp_start":[0.48022,0.04446,0.13848],"tcp_to_object_dist_end":0.03877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48279,0.0478,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29085,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15615,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7693.0,"raw_peak_contact_force":0.20707,"subtask_id":"grasp_reach","tcp_end":[0.46984,0.04683,0.05585],"tcp_start":[0.47788,0.0476,0.06447],"tcp_to_object_dist_end":0.03296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.47189,0.06854,0.13789],"object_pos_start":[0.48279,0.0478,0.02556],"object_to_goal_dist_end":0.21534,"object_to_goal_dist_start":0.29085,"object_z_max":0.15991,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11662.0,"raw_peak_contact_force":0.25611,"subtask_id":"lift_clear","tcp_end":[0.47863,0.0474,0.21448],"tcp_start":[0.46984,0.04683,0.05585],"tcp_to_object_dist_end":0.07974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47754,0.09143,0.01602],"object_pos_start":[0.47189,0.06854,0.13789],"object_to_goal_dist_end":0.27526,"object_to_goal_dist_start":0.21534,"object_z_max":0.13789,"peak_contact_force":9748.78521,"phase_name":"secure_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3965.0,"raw_peak_contact_force":1.86433,"subtask_id":"grasp_reach","tcp_end":[0.47318,0.04688,0.20616],"tcp_start":[0.47318,0.04688,0.20616],"tcp_to_object_dist_end":0.19534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47754,0.09143,0.01602],"object_pos_start":[0.47754,0.09143,0.01602],"object_to_goal_dist_end":0.27526,"object_to_goal_dist_start":0.27526,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.4731,0.04688,0.20603],"tcp_start":[0.47314,0.04688,0.20609],"tcp_to_object_dist_end":0.19522,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.47754,0.09143,0.01602],"object_pos_start":[0.47754,0.09143,0.01602],"object_to_goal_dist_end":0.27526,"object_to_goal_dist_start":0.27526,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57407,0.21977,0.2229],"tcp_start":[0.4731,0.04688,0.20603],"tcp_to_object_dist_end":0.26189,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28169,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.26128,"descend_grasp.descend_grasp_speed":0.0442,"descend_place.place_descent_z":-0.0005,"descend_place.place_speed":0.04177,"lift.lift_height":0.22549,"lift.lift_speed":0.11071,"transport.transport_arc_height":0.01247,"transport.transport_overhead":0.13936,"transport.transport_speed":0.10152},"optimized_scores":{"best_composite_score":-0.06743,"best_fitness_score":0.53257,"best_task_score":0.16},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.53633,0.04292,-0.00268],"force_p95":0.3877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9559,"mean_force":0.17098,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.52784,-0.02112,0.22211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5454.0,"contact_point_centroid":[0.5261,-0.03958,0.12357],"force_p95":0.1552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38176,"mean_force":0.10166,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52475,-0.02097,0.12719]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.5354,-0.02122,-0.0014],"force_p95":0.26515,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33474,"mean_force":0.06672,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52157,-0.02083,0.0551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6938.0,"contact_point_centroid":[0.52692,-0.00316,0.13331],"force_p95":0.1318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30162,"mean_force":0.08386,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5255,-0.02099,0.13697]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02135,-0.00207],"force_p95":0.13766,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.161,"mean_force":0.12806,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52384,-0.02086,0.05514]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51397,-0.00968,0.21781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3191.0,"contact_point_centroid":[0.52433,-0.03967,0.05162],"force_p95":0.1152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12488,"mean_force":0.06837,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52262,-0.02084,0.05369]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52926,-0.02026,0.10014]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53505,0.04537,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52771,-0.02112,0.22189]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53505,0.04537,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56326,0.09514,0.20807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7.0,"contact_point_centroid":[0.53213,-0.00923,0.22559],"force_p95":0.11325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11747,"mean_force":0.05485,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.53315,-0.02124,0.23189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3400.0,"contact_point_centroid":[0.52465,-0.00227,0.05111],"force_p95":0.09675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10885,"mean_force":0.06178,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52262,-0.02084,0.05369]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1854.0,"contact_point_centroid":[0.52799,-0.02111,0.22454],"force_p95":0.01151,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01037,"phase_index":4.0,"phase_name":"secure_grasp","phase_type":"grasp","tcp_position_centroid":[0.5278,-0.02112,0.22206]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4303.0,"contact_point_centroid":[0.56334,0.09514,0.21043],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01037,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56328,0.09522,0.20806]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12.0,"contact_point_centroid":[0.52793,-0.02111,0.22397],"force_p95":0.01079,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01079,"mean_force":0.01076,"phase_index":5.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52771,-0.02112,0.22189]}],"total_contact_groups":15},"final_pose_error":0.02686,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53505,0.04537,0.01602],"final_tcp_position":[0.59946,0.20415,0.20011],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9749.10322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53012,-0.01964,0.13687],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.53108,-0.02096,0.06388],"tcp_start":[0.53012,-0.01964,0.13687],"tcp_to_object_dist_end":0.03832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53708,-0.02133,0.02562],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31694,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14061,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8391.0,"raw_peak_contact_force":0.161,"subtask_id":"grasp_reach","tcp_end":[0.52259,-0.02084,0.05365],"tcp_start":[0.53108,-0.02096,0.06388],"tcp_to_object_dist_end":0.03156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.53677,-0.01178,0.18823],"object_pos_start":[0.53708,-0.02133,0.02562],"object_to_goal_dist_end":0.2513,"object_to_goal_dist_start":0.31694,"object_z_max":0.18843,"peak_contact_force":0.07168,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12477.0,"raw_peak_contact_force":0.38176,"subtask_id":"lift_clear","tcp_end":[0.53308,-0.02124,0.23179],"tcp_start":[0.52259,-0.02084,0.05365],"tcp_to_object_dist_end":0.04473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.53505,0.04537,0.01602],"object_pos_start":[0.53677,-0.01178,0.18823],"object_to_goal_dist_end":0.27488,"object_to_goal_dist_start":0.2513,"object_z_max":0.18823,"peak_contact_force":0.12263,"phase_name":"secure_grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3501.0,"raw_peak_contact_force":1.9559,"subtask_id":"grasp_reach","tcp_end":[0.52773,-0.02112,0.22192],"tcp_start":[0.52773,-0.02112,0.22192],"tcp_to_object_dist_end":0.21649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53505,0.04537,0.01602],"object_pos_start":[0.53505,0.04537,0.01602],"object_to_goal_dist_end":0.27488,"object_to_goal_dist_start":0.27488,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.52765,-0.02112,0.22177],"tcp_start":[0.52769,-0.02112,0.22184],"tcp_to_object_dist_end":0.21636,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53505,0.04537,0.01602],"object_pos_start":[0.53505,0.04537,0.01602],"object_to_goal_dist_end":0.27488,"object_to_goal_dist_start":0.27488,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8303.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59946,0.20415,0.20011],"tcp_start":[0.52765,-0.02112,0.22177],"tcp_to_object_dist_end":0.2515,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```