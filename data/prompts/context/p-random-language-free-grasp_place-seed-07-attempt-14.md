## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1585 | 0.18 | ❌ rejected |
| 13 | approach → descend → grasp → lift → grasp → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | -0.0576 | 0.18 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0907 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3541 | 0.62 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2105 | 0.54 | ❌ rejected |

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

## Current Skill (Q=-0.158) — your mutation base

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

- **Composite score**: -0.158
- **task_score** (E): 0.180
- **fitness_score**: 0.292  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1683 |
| descend_grasp | 1.00 | 1.00 | 0.0735 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.0253 |
| transport | 0.33 | 1.00 | 0.2346 |
| descend_place | 1.00 | 1.00 | 0.1022 |
| release | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.505, 0.022, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.505, 0.022, 0.064)→(0.497, 0.021, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 29.667 | 0.150 | 0.190 |
| lift | lift | 1.00 / step_budget | (0.492, 0.029, 0.077)→(0.497, 0.030, 0.100) | (0.511, 0.022, 0.026)→(0.500, 0.030, 0.045) | 0.274→0.263 | 1.00 / 16.000 | 146986.120 | 0.401 |
| transport | approach | 0.33 / step_budget | (0.497, 0.030, 0.100)→(0.573, 0.167, 0.271) | (0.499, 0.032, 0.044)→(0.494, 0.056, 0.019) | 0.262→0.261 | 1.00 / 8.333 | 6499.266 | 0.730 |
| descend_place | descend | 1.00 / step_budget | (0.573, 0.167, 0.271)→(0.601, 0.205, 0.188) | (0.494, 0.056, 0.019)→(0.494, 0.056, 0.019) | 0.261→0.261 | 1.00 / 8.333 | 3249.704 | 0.123 |
| release | release | 1.00 / step_budget | (0.601, 0.205, 0.188)→(0.595, 0.203, 0.209) | (0.494, 0.056, 0.019)→(0.494, 0.056, 0.019) | 0.261→0.261 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.240
- phase_score: 0.565
- phase_breakdown.place_goal_score: 0.859
- phase_breakdown.approach_goal_score: 0.120
- phase_breakdown.grasp_reach_score: 0.745
- phase_breakdown.lift_clear_score: 0.153
- phase_breakdown.approach_object_score: 0.820
- phase_breakdown.release_score: 0.590
- grasp_place_fitness: 0.322

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.322
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.240
- **Median Q (composite search score)**: -0.173
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_place.place_descent_z
- **Final σ (mean)**: 0.492


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86087,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.11214,"descend_place.place_descent_z":0.00928,"lift.lift_height":0.06971,"release.release_duration":1.73637,"transport.transport_overhead":0.19603,"transport.transport_speed":0.1763},"optimized_scores":{"best_composite_score":-0.1284,"best_fitness_score":0.3216,"best_task_score":0.23982},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3710.0,"contact_point_centroid":[0.50131,0.05662,-0.00209],"force_p95":0.12439,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68608,"mean_force":0.13062,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53466,0.07333,0.14718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.50694,0.05743,0.08147],"force_p95":0.24952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36046,"mean_force":0.12128,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5069,0.03912,0.08705]},{"body_a":"world","body_b":"grasp_target","contact_count":281.0,"contact_point_centroid":[0.51148,0.03742,-0.00113],"force_p95":0.14312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25543,"mean_force":0.05191,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49808,0.03803,0.05669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5265.0,"contact_point_centroid":[0.50068,0.05684,0.0662],"force_p95":0.13761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24461,"mean_force":0.08417,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50126,0.0382,0.06932]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03971,-0.00211],"force_p95":0.15503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20159,"mean_force":0.13091,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50005,0.03822,0.05612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3133.0,"contact_point_centroid":[0.49938,0.01942,0.05136],"force_p95":0.10039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1757,"mean_force":0.06605,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49886,0.03812,0.05477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5289.0,"contact_point_centroid":[0.50178,0.01991,0.06539],"force_p95":0.12572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17401,"mean_force":0.0807,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5012,0.0382,0.0691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":337.0,"contact_point_centroid":[0.50811,0.02308,0.08282],"force_p95":0.13107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16854,"mean_force":0.0569,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5071,0.03981,0.08785]},{"body_a":"world","body_b":"grasp_target","contact_count":2056.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50267,0.01774,0.21882]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.03742,0.10081]},{"body_a":"world","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.50129,0.05725,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5937,0.13956,0.16876]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50129,0.05725,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61677,0.16794,0.14811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3009.0,"contact_point_centroid":[0.49808,0.05705,0.05229],"force_p95":0.09982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1004,"mean_force":0.06942,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49887,0.03812,0.05478]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3598.0,"contact_point_centroid":[0.53761,0.07623,0.15514],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01483,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53732,0.07627,0.15267]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3145.0,"contact_point_centroid":[0.59363,0.13935,0.17118],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59364,0.13949,0.16881]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.61981,0.16866,0.14657],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61968,0.1688,0.14439]}],"total_contact_groups":16},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50129,0.05725,0.01602],"final_tcp_position":[0.6212,0.16913,0.14739],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2056.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50754,0.03627,0.13784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50712,0.03878,0.06424],"tcp_start":[0.50754,0.03627,0.13784],"tcp_to_object_dist_end":0.03861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51256,0.03899,0.02561],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21288,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1521,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7942.0,"raw_peak_contact_force":0.20159,"subtask_id":"grasp_reach","tcp_end":[0.49883,0.03812,0.05474],"tcp_start":[0.50712,0.03878,0.06424],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.50942,0.03901,0.05045],"object_pos_start":[0.51256,0.03899,0.02561],"object_to_goal_dist_end":0.20181,"object_to_goal_dist_start":0.21288,"object_z_max":0.05043,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.25543,"subtask_id":"lift_clear","tcp_end":[0.50683,0.03855,0.08631],"tcp_start":[0.49883,0.03812,0.05474],"tcp_to_object_dist_end":0.03595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50129,0.05725,0.01602],"object_pos_start":[0.50942,0.03901,0.05045],"object_to_goal_dist_end":0.21418,"object_to_goal_dist_start":0.20181,"object_z_max":0.05049,"peak_contact_force":9748.87049,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7809.0,"raw_peak_contact_force":0.68608,"subtask_id":"approach_goal","tcp_end":[0.56125,0.10221,0.20161],"tcp_start":[0.50683,0.03855,0.08631],"tcp_to_object_dist_end":0.20015,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50129,0.05725,0.01602],"object_pos_start":[0.50129,0.05725,0.01602],"object_to_goal_dist_end":0.21418,"object_to_goal_dist_start":0.21418,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6089.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6212,0.16913,0.14739],"tcp_start":[0.56125,0.10221,0.20161],"tcp_to_object_dist_end":0.21012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50129,0.05725,0.01602],"object_pos_start":[0.50129,0.05725,0.01602],"object_to_goal_dist_end":0.21418,"object_to_goal_dist_start":0.21418,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release","tcp_end":[0.61504,0.16743,0.16771],"tcp_start":[0.6212,0.16913,0.14739],"tcp_to_object_dist_end":0.21928,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70068,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17538,"descend_place.place_descent_z":-0.05,"lift.lift_height":0.0852,"release.release_duration":0.98062,"transport.transport_overhead":0.11236,"transport.transport_speed":0.49576},"optimized_scores":{"best_composite_score":-0.17445,"best_fitness_score":0.27555,"best_task_score":0.14969},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1703.0,"contact_point_centroid":[0.45747,0.07274,-0.00213],"force_p95":0.33084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70513,"mean_force":0.13468,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46602,0.05647,0.10321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4307.0,"contact_point_centroid":[0.46905,0.06526,0.0683],"force_p95":0.1312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28226,"mean_force":0.08606,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4707,0.04681,0.07192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3895.0,"contact_point_centroid":[0.47077,0.02829,0.06654],"force_p95":0.13319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20836,"mean_force":0.08765,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4705,0.04679,0.0709]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04869,-0.00213],"force_p95":0.15937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20701,"mean_force":0.13187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47102,0.04695,0.05709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2890.0,"contact_point_centroid":[0.47036,0.02815,0.05174],"force_p95":0.10872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17572,"mean_force":0.07112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46987,0.04684,0.05587]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48934,0.02173,0.2192]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45283,0.0782,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50463,0.13811,0.21099]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47792,0.04592,0.10132]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.45283,0.0782,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56811,0.21524,0.24671]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45283,0.0782,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57219,0.22342,0.18847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3003.0,"contact_point_centroid":[0.46834,0.06571,0.05259],"force_p95":0.10185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10251,"mean_force":0.06957,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46987,0.04684,0.05588]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1283.0,"contact_point_centroid":[0.46393,0.06032,0.11467],"force_p95":0.01215,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01073,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46317,0.06029,0.11268]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4270.0,"contact_point_centroid":[0.50512,0.13837,0.21372],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01044,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50491,0.13844,0.21145]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.57423,0.22405,0.18639],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57456,0.22439,0.18412]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1516.0,"contact_point_centroid":[0.56796,0.21503,0.24891],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01028,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56814,0.21528,0.24649]}],"total_contact_groups":15},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.45283,0.0782,0.02602],"final_tcp_position":[0.57617,0.22497,0.18765],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.47275,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48019,0.04447,0.1384],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":948.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47788,0.0476,0.06446],"tcp_start":[0.48019,0.04447,0.1384],"tcp_to_object_dist_end":0.03875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48279,0.0478,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29085,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15611,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7693.0,"raw_peak_contact_force":0.20701,"subtask_id":"grasp_reach","tcp_end":[0.46984,0.04684,0.05584],"tcp_start":[0.47788,0.0476,0.06446],"tcp_to_object_dist_end":0.03295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":793.0,"n_steps_budget":600.0,"object_pos_end":[0.45703,0.07308,0.02656],"object_pos_start":[0.48279,0.0478,0.02556],"object_to_goal_dist_end":0.28537,"object_to_goal_dist_start":0.29085,"object_z_max":0.05053,"peak_contact_force":273006.47275,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11188.0,"raw_peak_contact_force":0.70513,"subtask_id":"lift_clear","tcp_end":[0.45249,0.07215,0.12337],"tcp_start":[0.45575,0.06906,0.12272],"tcp_to_object_dist_end":0.09692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45283,0.0782,0.02602],"object_pos_start":[0.45283,0.0782,0.02602],"object_to_goal_dist_end":0.28487,"object_to_goal_dist_start":0.28487,"object_z_max":0.02602,"peak_contact_force":9748.80566,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8270.0,"raw_peak_contact_force":0.12268,"subtask_id":"approach_goal","tcp_end":[0.56214,0.20678,0.30573],"tcp_start":[0.45249,0.07215,0.12337],"tcp_to_object_dist_end":0.32668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.45283,0.0782,0.02602],"object_pos_start":[0.45283,0.0782,0.02602],"object_to_goal_dist_end":0.28487,"object_to_goal_dist_start":0.28487,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57617,0.22497,0.18765],"tcp_start":[0.56214,0.20678,0.30573],"tcp_to_object_dist_end":0.25075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45283,0.0782,0.02602],"object_pos_start":[0.45283,0.0782,0.02602],"object_to_goal_dist_end":0.28487,"object_to_goal_dist_start":0.28487,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release","tcp_end":[0.57078,0.22282,0.20842],"tcp_start":[0.57617,0.22497,0.18765],"tcp_to_object_dist_end":0.26096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44318,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03641,"descend_place.place_descent_z":0.01772,"lift.lift_height":0.07591,"release.release_duration":1.33114,"transport.transport_overhead":0.14299,"transport.transport_speed":0.43091},"optimized_scores":{"best_composite_score":-0.17265,"best_fitness_score":0.27735,"best_task_score":0.14941},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3271.0,"contact_point_centroid":[0.5268,0.03362,-0.00214],"force_p95":0.12494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38203,"mean_force":0.13224,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56746,0.10225,0.21332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1299.0,"contact_point_centroid":[0.53299,0.00654,0.09398],"force_p95":0.15067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42305,"mean_force":0.09144,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53172,-0.01079,0.09856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":752.0,"contact_point_centroid":[0.53342,-0.03006,0.09313],"force_p95":0.18052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3305,"mean_force":0.13473,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53155,-0.0117,0.0978]},{"body_a":"world","body_b":"grasp_target","contact_count":297.0,"contact_point_centroid":[0.53643,-0.02112,-0.0012],"force_p95":0.12801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24194,"mean_force":0.05771,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52159,-0.02085,0.05538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5341.0,"contact_point_centroid":[0.52595,-0.03969,0.06695],"force_p95":0.13797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21425,"mean_force":0.08653,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52497,-0.021,0.07029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5985.0,"contact_point_centroid":[0.52638,-0.00301,0.06783],"force_p95":0.11681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18997,"mean_force":0.07568,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52523,-0.02101,0.07116]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02135,-0.00207],"force_p95":0.13826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1609,"mean_force":0.1283,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52384,-0.02086,0.05505]},{"body_a":"world","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51365,-0.00964,0.21801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3193.0,"contact_point_centroid":[0.52433,-0.03968,0.05155],"force_p95":0.11422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12436,"mean_force":0.06844,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52262,-0.02084,0.0536]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5294,-0.02027,0.10005]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.52665,0.03362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60033,0.2055,0.26775]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52665,0.03362,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60171,0.21958,0.23037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3401.0,"contact_point_centroid":[0.52465,-0.00226,0.05104],"force_p95":0.09669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10877,"mean_force":0.06209,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52262,-0.02084,0.0536]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3175.0,"contact_point_centroid":[0.57035,0.11092,0.22473],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57035,0.11101,0.22239]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1058.0,"contact_point_centroid":[0.5999,0.20515,0.27027],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01258,"mean_force":0.01029,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6003,0.20542,0.26796]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.60349,0.22021,0.22864],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60376,0.22047,0.22646]}],"total_contact_groups":16},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52665,0.03362,0.01602],"final_tcp_position":[0.6052,0.22079,0.23012],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.86629,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2376.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53013,-0.01964,0.13675],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":908.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.53109,-0.02096,0.0638],"tcp_start":[0.53013,-0.01964,0.13675],"tcp_to_object_dist_end":0.03825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53707,-0.02133,0.02559],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31696,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14153,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8394.0,"raw_peak_contact_force":0.1609,"subtask_id":"grasp_reach","tcp_end":[0.52259,-0.02084,0.05357],"tcp_start":[0.53109,-0.02096,0.0638],"tcp_to_object_dist_end":0.0315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":478.0,"n_steps_budget":600.0,"object_pos_end":[0.5349,-0.02142,0.05683],"object_pos_start":[0.53707,-0.02133,0.02559],"object_to_goal_dist_end":0.30075,"object_to_goal_dist_start":0.31696,"object_z_max":0.05678,"peak_contact_force":0.15678,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11623.0,"raw_peak_contact_force":0.24194,"subtask_id":"lift_clear","tcp_end":[0.53124,-0.02121,0.09145],"tcp_start":[0.52259,-0.02084,0.05357],"tcp_to_object_dist_end":0.03481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,0.03362,0.01602],"object_pos_start":[0.5349,-0.02142,0.05683],"object_to_goal_dist_end":0.28516,"object_to_goal_dist_start":0.30075,"object_z_max":0.06898,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8497.0,"raw_peak_contact_force":1.38203,"subtask_id":"approach_goal","tcp_end":[0.59707,0.19193,0.30589],"tcp_start":[0.53124,-0.02121,0.09145],"tcp_to_object_dist_end":0.33771,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,0.03362,0.01602],"object_pos_start":[0.52665,0.03362,0.01602],"object_to_goal_dist_end":0.28516,"object_to_goal_dist_start":0.28516,"object_z_max":0.01602,"peak_contact_force":9748.86629,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2034.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6052,0.22079,0.23012],"tcp_start":[0.59707,0.19193,0.30589],"tcp_to_object_dist_end":0.29503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52665,0.03362,0.01602],"object_pos_start":[0.52665,0.03362,0.01602],"object_to_goal_dist_end":0.28516,"object_to_goal_dist_start":0.28516,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release","tcp_end":[0.60052,0.21905,0.25001],"tcp_start":[0.6052,0.22079,0.23012],"tcp_to_object_dist_end":0.30755,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```