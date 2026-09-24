## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1507 | 0.33 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5718 | 0.95 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1885 | 0.31 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.151) — your mutation base

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

- **Composite score**: 0.151
- **task_score** (E): 0.331
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1682 |
| descend_grasp | 1.00 | 1.00 | 0.0847 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 0.67 | 1.00 | 0.1623 |
| transport | 1.00 | 0.67 | 0.2095 |
| descend_place | 1.00 | 1.00 | 0.0713 |
| release_place | 1.00 | 1.00 | 0.0209 |
| retract_away | 1.00 | 1.00 | 0.0909 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.053) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.022, 0.053)→(0.497, 0.022, 0.044) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 45.667 | 0.147 | 0.184 |
| lift | lift | 0.67 / step_budget | (0.497, 0.022, 0.044)→(0.504, 0.022, 0.206) | (0.511, 0.022, 0.026)→(0.512, 0.022, 0.181) | 0.273→0.217 | 1.00 / 39.333 | 0.085 | 0.479 |
| transport | approach | 1.00 / step_budget | (0.504, 0.022, 0.206)→(0.593, 0.188, 0.286) | (0.512, 0.022, 0.181)→(0.588, 0.196, 0.211) | 0.217→0.082 | 0.67 / 21.333 | 84.230 | 0.391 |
| descend_place | descend | 1.00 / step_budget | (0.593, 0.188, 0.286)→(0.601, 0.205, 0.219) | (0.588, 0.196, 0.211)→(0.596, 0.209, 0.122) | 0.082→0.075 | 1.00 / 23.000 | 3249.729 | 0.996 |
| release_place | release | 1.00 / step_budget | (0.601, 0.205, 0.219)→(0.596, 0.203, 0.239) | (0.596, 0.209, 0.122)→(0.588, 0.205, 0.025) | 0.075→0.171 | 1.00 / 4.000 | 0.117 | 1.019 |
| retract_away | retract | 1.00 / step_budget | (0.596, 0.203, 0.239)→(0.604, 0.209, 0.330) | (0.588, 0.205, 0.025)→(0.585, 0.204, 0.026) | 0.171→0.170 | 1.00 / 4.000 | 0.123 | 0.141 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.444
- phase_score: 0.551
- phase_breakdown.place_goal_score: 0.360
- phase_breakdown.approach_goal_score: 0.335
- phase_breakdown.grasp_reach_score: 0.654
- phase_breakdown.lift_clear_score: 0.585
- phase_breakdown.approach_object_score: 0.822
- grasp_place_fitness: 0.688

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.688
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.444
- **Median Q (composite search score)**: 0.134
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.269


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09444,"descend_place.place_descent_z":0.02224,"lift.lift_height":0.21209,"release_place.release_duration":0.45037,"transport.transport_overhead":0.16987,"transport.transport_speed":0.3253},"optimized_scores":{"best_composite_score":0.20753,"best_fitness_score":0.68753,"best_task_score":0.44425},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":253.0,"contact_point_centroid":[0.60343,0.16477,-0.00548],"force_p95":0.98207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27313,"mean_force":0.2821,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.61623,0.16808,0.18514]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50998,0.03786,-0.0012],"force_p95":0.27679,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48993,"mean_force":0.06795,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49782,0.03843,0.04539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.61566,0.18774,0.16861],"force_p95":0.10309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31535,"mean_force":0.07128,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.62002,0.16922,0.17053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19434.0,"contact_point_centroid":[0.50091,0.05771,0.12545],"force_p95":0.07562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30634,"mean_force":0.05238,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50099,0.03854,0.12253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21046.0,"contact_point_centroid":[0.50242,0.01945,0.12137],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29762,"mean_force":0.04915,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50077,0.03852,0.11971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17931.0,"contact_point_centroid":[0.55908,0.07827,0.24727],"force_p95":0.08436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28754,"mean_force":0.05591,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55757,0.09737,0.24762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4528.0,"contact_point_centroid":[0.6113,0.18142,0.23812],"force_p95":0.10925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28422,"mean_force":0.0726,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6164,0.16343,0.23953]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":849.0,"contact_point_centroid":[0.62385,0.15128,0.16553],"force_p95":0.09319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27445,"mean_force":0.06232,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.62002,0.16923,0.17054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18919.0,"contact_point_centroid":[0.55438,0.11625,0.24843],"force_p95":0.07681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26242,"mean_force":0.05227,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55777,0.0976,0.24779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4325.0,"contact_point_centroid":[0.6192,0.14541,0.23089],"force_p95":0.11458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24769,"mean_force":0.07685,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61681,0.1639,0.23455]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.0398,-0.00211],"force_p95":0.1534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20062,"mean_force":0.13092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50042,0.03866,0.0449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5551.0,"contact_point_centroid":[0.50049,0.01931,0.04579],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16817,"mean_force":0.04016,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04354]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.60328,0.16483,-0.00197],"force_p95":0.13061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14897,"mean_force":0.12207,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.61887,0.1694,0.2352]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50263,0.01778,0.21861]},{"body_a":"world","body_b":"grasp_target","contact_count":2712.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50613,0.03795,0.08521]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5154.0,"contact_point_centroid":[0.49819,0.05778,0.04806],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07557,"mean_force":0.04278,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.03856,0.04354]}],"total_contact_groups":16},"final_pose_error":0.01523,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60327,0.16483,0.02602],"final_tcp_position":[0.62429,0.17147,0.28019],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":252.61741,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50758,0.0363,0.13772],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2712.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.50736,0.03922,0.05268],"tcp_start":[0.50758,0.0363,0.13772],"tcp_to_object_dist_end":0.02716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03926,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15277,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12505.0,"raw_peak_contact_force":0.20062,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.03855,0.0435],"tcp_start":[0.50736,0.03922,0.05268],"tcp_to_object_dist_end":0.02234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51479,0.03964,0.18173],"object_pos_start":[0.51251,0.03926,0.0256],"object_to_goal_dist_end":0.17811,"object_to_goal_dist_start":0.21274,"object_z_max":0.18154,"peak_contact_force":0.0839,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40625.0,"raw_peak_contact_force":0.48993,"subtask_id":"lift_clear","tcp_end":[0.50726,0.03888,0.20631],"tcp_start":[0.49917,0.03855,0.0435],"tcp_to_object_dist_end":0.02572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61422,0.16025,0.26539],"object_pos_start":[0.51479,0.03964,0.18173],"object_to_goal_dist_end":0.12172,"object_to_goal_dist_start":0.17811,"object_z_max":0.26531,"peak_contact_force":252.61741,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36850.0,"raw_peak_contact_force":0.28754,"subtask_id":"approach_goal","tcp_end":[0.61337,0.15872,0.29599],"tcp_start":[0.50726,0.03888,0.20631],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.62085,0.172,0.14214],"object_pos_start":[0.61422,0.16025,0.26539],"object_to_goal_dist_end":0.00733,"object_to_goal_dist_start":0.12172,"object_z_max":0.26539,"peak_contact_force":0.10629,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8853.0,"raw_peak_contact_force":0.28422,"subtask_id":"place_goal","tcp_end":[0.6221,0.16977,0.17501],"tcp_start":[0.61337,0.15872,0.29599],"tcp_to_object_dist_end":0.03297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60596,0.16562,0.02597],"object_pos_start":[0.62085,0.172,0.14214],"object_to_goal_dist_end":0.1212,"object_to_goal_dist_start":0.00733,"object_z_max":0.14214,"peak_contact_force":0.0979,"phase_name":"release_place","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1822.0,"raw_peak_contact_force":1.27313,"subtask_id":"place_goal","tcp_end":[0.61616,0.16806,0.19465],"tcp_start":[0.6221,0.16977,0.17501],"tcp_to_object_dist_end":0.169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.60327,0.16483,0.02602],"object_pos_start":[0.60596,0.16562,0.02597],"object_to_goal_dist_end":0.1217,"object_to_goal_dist_start":0.1212,"object_z_max":0.02668,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.14897,"tcp_end":[0.62429,0.17147,0.28019],"tcp_start":[0.61616,0.16806,0.19465],"tcp_to_object_dist_end":0.25512,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83815,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06804,"descend_place.place_descent_z":0.01823,"lift.lift_height":0.28241,"release_place.release_duration":0.76805,"transport.transport_overhead":0.10155,"transport.transport_speed":0.27458},"optimized_scores":{"best_composite_score":0.11004,"best_fitness_score":0.59004,"best_task_score":0.2542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":448.0,"contact_point_centroid":[0.55813,0.23818,-0.00548],"force_p95":1.17007,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33381,"mean_force":0.29076,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57184,0.21597,0.27795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13686.0,"contact_point_centroid":[0.50925,0.13433,0.24863],"force_p95":0.10385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5857,"mean_force":0.06517,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51303,0.11628,0.24981]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11322.0,"contact_point_centroid":[0.51111,0.09077,0.24302],"force_p95":0.13149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48172,"mean_force":0.07892,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50902,0.10951,0.24535]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.48034,0.04659,-0.00121],"force_p95":0.23207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45222,"mean_force":0.06124,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46844,0.04715,0.0478]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19398.0,"contact_point_centroid":[0.46994,0.06632,0.12672],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28805,"mean_force":0.05261,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47006,0.04719,0.12486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19464.0,"contact_point_centroid":[0.4719,0.02816,0.12476],"force_p95":0.08514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2802,"mean_force":0.05311,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47003,0.04718,0.12435]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04878,-0.00212],"force_p95":0.156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20119,"mean_force":0.13162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47097,0.04742,0.04707]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56217,0.23271,-0.002],"force_p95":0.14772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18994,"mean_force":0.12238,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.57305,0.222,0.25538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.47165,0.02812,0.04667],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15942,"mean_force":0.04362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04584]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4892,0.02171,0.21918]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.56218,0.23269,-0.00199],"force_p95":0.12266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12306,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.57489,0.22426,0.31878]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47745,0.04627,0.092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46884,0.06652,0.04945],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07758,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46979,0.04731,0.04585]},{"body_a":"left_finger","body_b":"right_finger","contact_count":518.0,"contact_point_centroid":[0.57245,0.21717,0.27514],"force_p95":0.01368,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01085,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57264,0.2174,0.27273]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.57446,0.22249,0.25338],"force_p95":0.01084,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01086,"mean_force":0.00986,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.57491,0.22283,0.2511]}],"total_contact_groups":15},"final_pose_error":0.01443,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56218,0.23269,0.02602],"final_tcp_position":[0.57973,0.2277,0.36626],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9749.00744,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48016,0.04445,0.13847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.47771,0.04808,0.05415],"tcp_start":[0.48016,0.04445,0.13847],"tcp_to_object_dist_end":0.02857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04813,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15504,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.20119,"subtask_id":"grasp_reach","tcp_end":[0.46976,0.0473,0.04581],"tcp_start":[0.47771,0.04808,0.05415],"tcp_to_object_dist_end":0.02406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48066,0.04843,0.18064],"object_pos_start":[0.48274,0.04813,0.02556],"object_to_goal_dist_end":0.21279,"object_to_goal_dist_start":0.29066,"object_z_max":0.18045,"peak_contact_force":0.09733,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39002.0,"raw_peak_contact_force":0.45222,"subtask_id":"lift_clear","tcp_end":[0.47465,0.04749,0.20827],"tcp_start":[0.46976,0.0473,0.04581],"tcp_to_object_dist_end":0.02829,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55164,0.22715,0.14677],"object_pos_start":[0.48066,0.04843,0.18064],"object_to_goal_dist_end":0.08902,"object_to_goal_dist_start":0.21279,"object_z_max":0.26464,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25008.0,"raw_peak_contact_force":0.5857,"subtask_id":"approach_goal","tcp_end":[0.5677,0.20738,0.31056],"tcp_start":[0.47465,0.04749,0.20827],"tcp_to_object_dist_end":0.16575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.56331,0.23164,0.02552],"object_pos_start":[0.55164,0.22715,0.14677],"object_to_goal_dist_end":0.20582,"object_to_goal_dist_start":0.08902,"object_z_max":0.14677,"peak_contact_force":9749.00744,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":966.0,"raw_peak_contact_force":2.33381,"subtask_id":"place_goal","tcp_end":[0.57619,0.22321,0.25454],"tcp_start":[0.5677,0.20738,0.31056],"tcp_to_object_dist_end":0.22954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5622,0.23268,0.02602],"object_pos_start":[0.56331,0.23164,0.02552],"object_to_goal_dist_end":0.20545,"object_to_goal_dist_start":0.20582,"object_z_max":0.02604,"peak_contact_force":0.12308,"phase_name":"release_place","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.18994,"subtask_id":"place_goal","tcp_end":[0.57201,0.22152,0.2753],"tcp_start":[0.57619,0.22321,0.25454],"tcp_to_object_dist_end":0.24972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.56218,0.23269,0.02602],"object_pos_start":[0.5622,0.23268,0.02602],"object_to_goal_dist_end":0.20545,"object_to_goal_dist_start":0.20545,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.12306,"tcp_end":[0.57973,0.2277,0.36626],"tcp_start":[0.57201,0.22152,0.2753],"tcp_to_object_dist_end":0.34073,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99286,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.24015,"descend_place.place_descent_z":0.0252,"lift.lift_height":0.21395,"release_place.release_duration":0.55173,"transport.transport_overhead":0.05849,"transport.transport_speed":0.39306},"optimized_scores":{"best_composite_score":0.13439,"best_fitness_score":0.61439,"best_task_score":0.29512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.58997,0.21381,-0.00759],"force_p95":1.16312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59365,"mean_force":0.38399,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.60035,0.21917,0.24056]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.53375,-0.0211,-0.00112],"force_p95":0.35906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49502,"mean_force":0.07782,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52199,-0.02105,0.04399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3156.0,"contact_point_centroid":[0.59397,0.2273,0.23788],"force_p95":0.07439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37032,"mean_force":0.05351,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60122,0.20958,0.23726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21047.0,"contact_point_centroid":[0.52629,-0.00213,0.12313],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31781,"mean_force":0.04902,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52504,-0.02118,0.12119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18289.0,"contact_point_centroid":[0.52525,-0.04035,0.12447],"force_p95":0.07934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30975,"mean_force":0.05506,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52506,-0.02118,0.1216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18655.0,"contact_point_centroid":[0.56502,0.06947,0.22472],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30031,"mean_force":0.05408,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56327,0.08854,0.2244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":959.0,"contact_point_centroid":[0.59699,0.23854,0.22437],"force_p95":0.08364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26661,"mean_force":0.05433,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.60348,0.22055,0.22422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19899.0,"contact_point_centroid":[0.55912,0.10338,0.22461],"force_p95":0.07308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26409,"mean_force":0.04976,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56204,0.08471,0.22349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3173.0,"contact_point_centroid":[0.60548,0.19102,0.23529],"force_p95":0.07645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22099,"mean_force":0.05355,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60124,0.20964,0.23722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1025.0,"contact_point_centroid":[0.60858,0.20233,0.22105],"force_p95":0.081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21194,"mean_force":0.05166,"phase_index":6.0,"phase_name":"release_place","phase_type":"release","tcp_position_centroid":[0.60346,0.22054,0.22416]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.59003,0.21379,-0.00199],"force_p95":0.12723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15212,"mean_force":0.12097,"phase_index":7.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.60302,0.22244,0.29308]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02144,-0.00203],"force_p95":0.13336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15067,"mean_force":0.12564,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52457,-0.02108,0.04379]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51397,-0.00968,0.21781]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52958,-0.02054,0.08476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5336.0,"contact_point_centroid":[0.52405,-0.00198,0.04433],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10082,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4161.0,"contact_point_centroid":[0.52255,-0.04032,0.04527],"force_p95":0.08072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.0516,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52331,-0.02106,0.04232]}],"total_contact_groups":16},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59003,0.21378,0.02602],"final_tcp_position":[0.60798,0.22648,0.34268],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.59365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53012,-0.01964,0.13687],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.5317,-0.02119,0.0522],"tcp_start":[0.53012,-0.01964,0.13687],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0215,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13351,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11297.0,"raw_peak_contact_force":0.15067,"subtask_id":"grasp_reach","tcp_end":[0.52328,-0.02106,0.04228],"tcp_start":[0.5317,-0.02119,0.0522],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53919,-0.02177,0.18061],"object_pos_start":[0.53692,-0.0215,0.02586],"object_to_goal_dist_end":0.26084,"object_to_goal_dist_start":0.31697,"object_z_max":0.18042,"peak_contact_force":0.07397,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39476.0,"raw_peak_contact_force":0.49502,"subtask_id":"lift_clear","tcp_end":[0.53126,-0.02136,0.20347],"tcp_start":[0.52328,-0.02106,0.04228],"tcp_to_object_dist_end":0.0242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59856,0.1992,0.22164],"object_pos_start":[0.53919,-0.02177,0.18061],"object_to_goal_dist_end":0.034,"object_to_goal_dist_start":0.26084,"object_z_max":0.22158,"peak_contact_force":0.07167,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38554.0,"raw_peak_contact_force":0.30031,"subtask_id":"approach_goal","tcp_end":[0.59837,0.19744,0.25045],"tcp_start":[0.53126,-0.02136,0.20347],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.60467,0.22296,0.19824],"object_pos_start":[0.59856,0.1992,0.22164],"object_to_goal_dist_end":0.01179,"object_to_goal_dist_start":0.034,"object_z_max":0.22164,"peak_contact_force":0.07323,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6329.0,"raw_peak_contact_force":0.37032,"subtask_id":"place_goal","tcp_end":[0.60494,0.22086,0.22781],"tcp_start":[0.59837,0.19744,0.25045],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5947,0.21637,0.02229],"object_pos_start":[0.60467,0.22296,0.19824],"object_to_goal_dist_end":0.18613,"object_to_goal_dist_start":0.01179,"object_z_max":0.19824,"peak_contact_force":0.13033,"phase_name":"release_place","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2178.0,"raw_peak_contact_force":1.59365,"subtask_id":"place_goal","tcp_end":[0.60031,0.21917,0.24799],"tcp_start":[0.60494,0.22086,0.22781],"tcp_to_object_dist_end":0.22578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.59003,0.21378,0.02602],"object_pos_start":[0.5947,0.21637,0.02229],"object_to_goal_dist_end":0.18306,"object_to_goal_dist_start":0.18613,"object_z_max":0.0268,"peak_contact_force":0.12263,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2532.0,"raw_peak_contact_force":0.15212,"tcp_end":[0.60798,0.22648,0.34268],"tcp_start":[0.60031,0.21917,0.24799],"tcp_to_object_dist_end":0.31742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```