## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2138 | 0.77 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1507 | 0.33 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5718 | 0.95 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.5951 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.214) — your mutation base

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

- **Composite score**: 0.214
- **task_score** (E): 0.767
- **fitness_score**: 0.834  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.67 | 1.00 | 0.1317 |
| descend_grasp | 1.00 | 1.00 | 0.1084 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 0.33 | 1.00 | 0.1274 |
| transport | 0.00 | 0.67 | 0.1572 |
| descend_place | 0.33 | 0.33 | 0.0320 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.016, 0.173) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 15.941 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.016, 0.173)→(0.506, 0.021, 0.065) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.021, 0.065)→(0.497, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.025) | 0.273→0.274 | 1.00 / 27.667 | 0.159 | 0.209 |
| lift | lift | 0.33 / step_budget | (0.497, 0.021, 0.056)→(0.506, 0.021, 0.183) | (0.511, 0.022, 0.025)→(0.520, 0.022, 0.151) | 0.274→0.215 | 1.00 / 22.000 | 0.141 | 0.336 |
| transport | approach | 0.00 / step_budget | (0.506, 0.021, 0.183)→(0.574, 0.140, 0.256) | (0.520, 0.022, 0.151)→(0.587, 0.144, 0.219) | 0.215→0.076 | 0.67 / 12.667 | 55983.966 | 0.337 |
| descend_place | descend | 0.33 / step_budget | (0.574, 0.140, 0.256)→(0.587, 0.163, 0.240) | (0.587, 0.144, 0.219)→(0.612, 0.177, 0.201) | 0.076→0.040 | 0.33 / 5.000 | 0.080 | 0.342 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.776
- phase_score: 0.490
- phase_breakdown.place_goal_score: 0.383
- phase_breakdown.approach_goal_score: 0.146
- phase_breakdown.grasp_reach_score: 0.770
- phase_breakdown.lift_clear_score: 0.615
- phase_breakdown.approach_object_score: 0.535
- grasp_place_fitness: 0.838

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.838
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.776
- **Median Q (composite search score)**: 0.217
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.369


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0303,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.11979,"approach_object.approach_tolerance":0.05695,"descend_grasp.descend_tolerance":0.01013,"descend_place.place_descent_z":-0.00255,"descend_place.place_tolerance":0.07469,"lift.lift_height":0.17451,"lift.lift_tolerance":0.04777,"transport.transport_overhead":0.13292,"transport.transport_speed":0.30194,"transport.transport_tolerance":0.08688},"optimized_scores":{"best_composite_score":0.21742,"best_fitness_score":0.83742,"best_task_score":0.77245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"left_finger","body_b":"grasp_target","contact_count":318.0,"contact_point_centroid":[0.59812,0.1103,0.21461],"force_p95":0.29379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56607,"mean_force":0.13911,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59192,0.12742,0.21989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":255.0,"contact_point_centroid":[0.59171,0.14526,0.21631],"force_p95":0.41856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51924,"mean_force":0.1614,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59195,0.12746,0.21983]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":813.0,"contact_point_centroid":[0.54657,0.05712,0.18119],"force_p95":0.30724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43021,"mean_force":0.15063,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54358,0.07507,0.18571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":759.0,"contact_point_centroid":[0.54356,0.09321,0.18161],"force_p95":0.26337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33429,"mean_force":0.1266,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54329,0.07476,0.18543]},{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51031,0.038,-0.00168],"force_p95":0.26996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32784,"mean_force":0.09785,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49804,0.03711,0.05625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.50004,0.05601,0.09573],"force_p95":0.15869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28536,"mean_force":0.09782,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50088,0.03734,0.09891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1469.0,"contact_point_centroid":[0.50152,0.01878,0.0944],"force_p95":0.17399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27173,"mean_force":0.10002,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50084,0.03734,0.09849]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51261,0.03968,-0.00218],"force_p95":0.17295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22246,"mean_force":0.13525,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50038,0.0373,0.05643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2886.0,"contact_point_centroid":[0.49978,0.01852,0.05111],"force_p95":0.1052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17899,"mean_force":0.07104,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49919,0.0372,0.05508]},{"body_a":"world","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.51251,0.03972,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12388,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50428,0.01166,0.2473]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50632,0.03188,0.12047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3050.0,"contact_point_centroid":[0.49836,0.05612,0.05253],"force_p95":0.10057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10131,"mean_force":0.06873,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4992,0.0372,0.05509]}],"total_contact_groups":12},"final_pose_error":0.0744,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62064,0.14368,0.16992],"final_tcp_position":[0.60155,0.13744,0.2027],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.56607,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12227,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50841,0.02569,0.18487],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15953,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_reach","tcp_end":[0.50746,0.03781,0.06457],"tcp_start":[0.50841,0.02569,0.18487],"tcp_to_object_dist_end":0.03893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51262,0.03843,0.0254],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21332,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1688,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7736.0,"raw_peak_contact_force":0.22246,"subtask_id":"grasp_reach","tcp_end":[0.49917,0.0372,0.05505],"tcp_start":[0.50746,0.03781,0.06457],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":125.0,"n_steps_budget":930.0,"object_pos_end":[0.51882,0.03909,0.12114],"object_pos_start":[0.51262,0.03843,0.0254],"object_to_goal_dist_end":0.17378,"object_to_goal_dist_start":0.21332,"object_z_max":0.12031,"peak_contact_force":0.12986,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3034.0,"raw_peak_contact_force":0.32784,"subtask_id":"lift_clear","tcp_end":[0.50657,0.03783,0.15283],"tcp_start":[0.49917,0.0372,0.05505],"tcp_to_object_dist_end":0.03399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.59573,0.12283,0.1895],"object_pos_start":[0.51882,0.03909,0.12114],"object_to_goal_dist_end":0.0739,"object_to_goal_dist_start":0.17378,"object_z_max":0.18863,"peak_contact_force":0.16804,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.43021,"subtask_id":"approach_goal","tcp_end":[0.58526,0.12047,0.22376],"tcp_start":[0.50657,0.03783,0.15283],"tcp_to_object_dist_end":0.0359,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":31.0,"n_steps_budget":1000.0,"object_pos_end":[0.62064,0.14368,0.16992],"object_pos_start":[0.59573,0.12283,0.1895],"object_to_goal_dist_end":0.03873,"object_to_goal_dist_start":0.0739,"object_z_max":0.19239,"peak_contact_force":0.23989,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":573.0,"raw_peak_contact_force":0.56607,"subtask_id":"place_goal","tcp_end":[0.60155,0.13744,0.2027],"tcp_start":[0.58526,0.12047,0.22376],"tcp_to_object_dist_end":0.03844,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91919,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.10093,"approach_object.approach_tolerance":0.03137,"descend_grasp.descend_tolerance":0.01049,"descend_place.place_descent_z":-0.00109,"descend_place.place_tolerance":0.04943,"lift.lift_height":0.25993,"lift.lift_tolerance":0.0828,"transport.transport_overhead":0.10587,"transport.transport_speed":0.07103,"transport.transport_tolerance":0.09984},"optimized_scores":{"best_composite_score":0.21793,"best_fitness_score":0.83793,"best_task_score":0.77605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.55289,0.18285,0.27625],"force_p95":0.42049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45886,"mean_force":0.1864,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55095,0.16328,0.27884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":272.0,"contact_point_centroid":[0.56325,0.15217,0.27162],"force_p95":0.21727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34922,"mean_force":0.09925,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55284,0.16698,0.27569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.47383,0.02761,0.11849],"force_p95":0.23364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32973,"mean_force":0.13062,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47237,0.0463,0.12285]},{"body_a":"world","body_b":"grasp_target","contact_count":61.0,"contact_point_centroid":[0.47965,0.04688,-0.00168],"force_p95":0.26626,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30925,"mean_force":0.15847,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46919,0.04605,0.05769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1442.0,"contact_point_centroid":[0.46927,0.06441,0.11498],"force_p95":0.20052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27299,"mean_force":0.10147,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47162,0.04624,0.11838]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":929.0,"contact_point_centroid":[0.51028,0.06695,0.22987],"force_p95":0.2251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26739,"mean_force":0.1451,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50499,0.08452,0.23416]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":890.0,"contact_point_centroid":[0.50573,0.10324,0.23071],"force_p95":0.20477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2371,"mean_force":0.12796,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5049,0.0844,0.23411]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04869,-0.00217],"force_p95":0.17115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21932,"mean_force":0.13493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47153,0.04628,0.05778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2890.0,"contact_point_centroid":[0.47072,0.02754,0.05208],"force_p95":0.10769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18201,"mean_force":0.07073,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04617,0.05656]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4919,0.01831,0.23221]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47972,0.04264,0.11123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2825.0,"contact_point_centroid":[0.46844,0.06507,0.05289],"force_p95":0.10715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10797,"mean_force":0.07397,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04617,0.05657]}],"total_contact_groups":12},"final_pose_error":0.04856,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.60037,0.19996,0.21407],"final_tcp_position":[0.56426,0.19104,0.25424],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":47.57832,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":792.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48367,0.03856,0.15952],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_reach","tcp_end":[0.4784,0.0469,0.06516],"tcp_start":[0.48367,0.03856,0.15952],"tcp_to_object_dist_end":0.03942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48283,0.0475,0.02542],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29112,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16633,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7515.0,"raw_peak_contact_force":0.21932,"subtask_id":"grasp_reach","tcp_end":[0.47036,0.04617,0.05653],"tcp_start":[0.4784,0.0469,0.06516],"tcp_to_object_dist_end":0.03354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,0.04795,0.17268],"object_pos_start":[0.48283,0.0475,0.02542],"object_to_goal_dist_end":0.20943,"object_to_goal_dist_start":0.29112,"object_z_max":0.17111,"peak_contact_force":0.1279,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2535.0,"raw_peak_contact_force":0.32973,"subtask_id":"lift_clear","tcp_end":[0.48021,0.04696,0.20415],"tcp_start":[0.47036,0.04617,0.05653],"tcp_to_object_dist_end":0.03421,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.56252,0.15955,0.24481],"object_pos_start":[0.49359,0.04795,0.17268],"object_to_goal_dist_end":0.07336,"object_to_goal_dist_start":0.20943,"object_z_max":0.24389,"peak_contact_force":167951.73011,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1819.0,"raw_peak_contact_force":0.26739,"subtask_id":"approach_goal","tcp_end":[0.54692,0.15563,0.2788],"tcp_start":[0.48021,0.04696,0.20415],"tcp_to_object_dist_end":0.03761,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.60037,0.19996,0.21407],"object_pos_start":[0.56252,0.15955,0.24481],"object_to_goal_dist_end":0.03803,"object_to_goal_dist_start":0.07336,"object_z_max":0.24842,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":451.0,"raw_peak_contact_force":0.45886,"subtask_id":"place_goal","tcp_end":[0.56426,0.19104,0.25424],"tcp_start":[0.54692,0.15563,0.2788],"tcp_to_object_dist_end":0.05475,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91525,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12568,"approach_object.approach_tolerance":0.04868,"descend_grasp.descend_tolerance":0.01248,"descend_place.place_descent_z":0.04181,"descend_place.place_tolerance":0.08193,"lift.lift_height":0.2328,"lift.lift_tolerance":0.06753,"transport.transport_overhead":0.10329,"transport.transport_speed":0.1003,"transport.transport_tolerance":0.09879},"optimized_scores":{"best_composite_score":0.20604,"best_fitness_score":0.82604,"best_task_score":0.75387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"left_finger","body_b":"grasp_target","contact_count":1411.0,"contact_point_centroid":[0.52429,-0.03913,0.10422],"force_p95":0.20309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34963,"mean_force":0.11151,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5236,-0.02044,0.10798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":672.0,"contact_point_centroid":[0.56021,0.02004,0.2154],"force_p95":0.25871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31419,"mean_force":0.17193,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55402,0.03764,0.21967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":777.0,"contact_point_centroid":[0.56176,0.06702,0.22081],"force_p95":0.22662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.297,"mean_force":0.13567,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5578,0.04914,0.22444]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.53441,-0.02065,-0.00159],"force_p95":0.25489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29583,"mean_force":0.11589,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52099,-0.02026,0.05744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1415.0,"contact_point_centroid":[0.52495,-0.0024,0.10879],"force_p95":0.19935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27207,"mean_force":0.10911,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52414,-0.02046,0.11293]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02129,-0.00209],"force_p95":0.1449,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18655,"mean_force":0.12966,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52351,-0.02029,0.05778]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.53702,-0.02132,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12362,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51218,-0.00686,0.24183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2972.0,"contact_point_centroid":[0.52241,-0.03907,0.05268],"force_p95":0.12192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12681,"mean_force":0.07216,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5223,-0.02027,0.05634]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5265,-0.01768,0.11833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2748.0,"contact_point_centroid":[0.52294,-0.00182,0.05215],"force_p95":0.10236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12236,"mean_force":0.07297,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5223,-0.02027,0.05634]}],"total_contact_groups":10},"final_pose_error":0.06936,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61422,0.18696,0.2182],"final_tcp_position":[0.59383,0.1619,0.26341],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.34963,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12257,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52525,-0.0149,0.17569],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_reach","tcp_end":[0.5308,-0.02036,0.06666],"tcp_start":[0.52525,-0.0149,0.17569],"tcp_to_object_dist_end":0.04113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53722,-0.02094,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31662,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14203,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7520.0,"raw_peak_contact_force":0.18655,"subtask_id":"grasp_reach","tcp_end":[0.52227,-0.02027,0.0563],"tcp_start":[0.5308,-0.02036,0.06666],"tcp_to_object_dist_end":0.03415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.54614,-0.02126,0.15903],"object_pos_start":[0.53722,-0.02094,0.0256],"object_to_goal_dist_end":0.26166,"object_to_goal_dist_start":0.31662,"object_z_max":0.15781,"peak_contact_force":0.16523,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.34963,"subtask_id":"lift_clear","tcp_end":[0.53226,-0.02075,0.19198],"tcp_start":[0.52227,-0.02027,0.0563],"tcp_to_object_dist_end":0.03575,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.60208,0.15046,0.22301],"object_pos_start":[0.54614,-0.02126,0.15903],"object_to_goal_dist_end":0.07928,"object_to_goal_dist_start":0.26166,"object_z_max":0.22284,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1449.0,"raw_peak_contact_force":0.31419,"subtask_id":"approach_goal","tcp_end":[0.58941,0.14453,0.26466],"tcp_start":[0.53226,-0.02075,0.19198],"tcp_to_object_dist_end":0.04393,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.61422,0.18696,0.2182],"object_pos_start":[0.60208,0.15046,0.22301],"object_to_goal_dist_end":0.04238,"object_to_goal_dist_start":0.07928,"object_z_max":0.2233,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_goal","tcp_end":[0.59383,0.1619,0.26341],"tcp_start":[0.58941,0.14453,0.26466],"tcp_to_object_dist_end":0.05557,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```