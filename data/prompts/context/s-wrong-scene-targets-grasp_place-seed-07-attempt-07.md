## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.3825 | 0.14 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4371 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0099 | 0.32 | ✅ accepted |
| 4 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.5365 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5125095466604667, 0.039721380096957554, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5125095466604667, 0.039721380096957554, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.382) — your mutation base

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
  - 0.15
  weight: 0.3
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
phases:
- id: approach_pre_grasp
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_success
    when: during_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: continue
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.1
      - 2.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: lift_object
- id: approach_goal
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
    - 0.2
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_success, when=during_phase, predicate=pose_within_tolerance, on_failure=continue, threshold=0.02
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=reduce_speed
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.382
- **task_score** (E): 0.145
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_approach_object | 0.00 | 1.00 | 0.2012 |
| contact_descend | 1.00 | 1.00 | 0.0000 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift_object_up | 1.00 | 1.00 | 0.0011 |
| arc_approach_goal | 0.00 | 1.00 | 0.1643 |
| descend_place | 0.00 | 1.00 | 0.0773 |
| release | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.412, -0.011, 0.131) | (0.511, 0.022, 0.030)→(0.470, 0.024, 0.016) | 0.271→0.295 | 1.00 / 5.000 | 201.409 | 1411.242 |
| contact_descend | descend | 1.00 / force_exceeded | (0.412, -0.011, 0.131)→(0.412, -0.011, 0.131) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.295→0.295 | 1.00 / 5.000 | 200.789 | 179.961 |
| grasp | grasp | 1.00 / step_budget | (0.412, -0.011, 0.130)→(0.412, -0.011, 0.130) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.295→0.295 | 1.00 / 9.333 | 91046.815 | 105.055 |
| lift_object_up | lift | 1.00 / step_budget | (0.464, 0.022, 0.217)→(0.465, 0.022, 0.218) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.295→0.295 | 1.00 / 8.333 | 3269.562 | 166.164 |
| arc_approach_goal | approach | 0.00 / step_budget | (0.465, 0.022, 0.218)→(0.507, 0.069, 0.367) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.295→0.295 | 1.00 / 8.333 | 3267.399 | 39.517 |
| descend_place | descend | 0.00 / step_budget | (0.507, 0.069, 0.367)→(0.536, 0.106, 0.310) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.295→0.295 | 1.00 / 8.667 | 3409.169 | 244.326 |
| release | release | 1.00 / step_budget | (0.536, 0.106, 0.310)→(0.537, 0.106, 0.331) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.295→0.295 | 1.00 / 4.667 | 30.237 | 145.479 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.203
- phase_score: 0.082
- phase_breakdown.approach_object_score: 0.053
- phase_breakdown.grasp_object_score: 0.051
- phase_breakdown.lift_object_score: 0.238
- phase_breakdown.place_at_goal_score: 0.028
- grasp_place_fitness: 0.196

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.196
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.203
- **Median Q (composite search score)**: -0.390
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.353


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
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":86.0,"average_failure_rate":0.26625,"average_mean_iterations":56.28173,"average_solve_count":323.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach_goal.arc_height":0.12616,"arc_approach_goal.speed":0.05183,"arc_approach_object.arc_height":0.1181,"arc_approach_object.speed":0.0203,"contact_descend.force_threshold":6.73367,"contact_descend.speed":0.02885,"descend_place.speed":0.03571,"grasp.grasp_duration":0.9021,"lift_object_up.lift_height":0.17751,"lift_object_up.speed":0.03354,"release.release_duration":0.37878},"optimized_scores":{"best_composite_score":-0.36156,"best_fitness_score":0.19558,"best_task_score":0.20306},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63537,0.01848,-0.00046],"force_p95":196.77022,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1552.10831,"mean_force":202.45703,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.39203,0.01809,0.12]},{"body_a":"link5","body_b":"hand","contact_count":329.0,"contact_point_centroid":[0.55178,0.02004,0.3044],"force_p95":286.21367,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.95528,"mean_force":247.7887,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52856,0.11083,0.32338]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.63116,0.02251,-0.0001],"force_p95":272.33233,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.3346,"mean_force":189.82983,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.39747,0.02397,0.14114]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54853,0.02617,0.27],"force_p95":172.05649,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.35218,"mean_force":97.4786,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53723,0.11745,0.31036]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63004,0.02264,-0.00025],"force_p95":95.22685,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.22685,"mean_force":95.22685,"phase_index":1.0,"phase_name":"contact_descend","phase_type":"descend","tcp_position_centroid":[0.39673,0.02406,0.14147]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63087,0.02254,-0.00013],"force_p95":82.88301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.72691,"mean_force":71.92596,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39716,0.02397,0.14105]},{"body_a":"grasp_target","body_b":"link7","contact_count":271.0,"contact_point_centroid":[0.49365,0.02154,0.03554],"force_p95":1.08029,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.49676,"mean_force":0.56254,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.38816,0.01436,0.09882]},{"body_a":"grasp_target","body_b":"hand","contact_count":231.0,"contact_point_centroid":[0.48438,0.02199,0.05105],"force_p95":2.24316,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.64196,"mean_force":0.54218,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.38776,0.01415,0.09601]},{"body_a":"world","body_b":"grasp_target","contact_count":3418.0,"contact_point_centroid":[0.48099,0.04489,-0.00274],"force_p95":0.41834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32815,"mean_force":0.18464,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.40645,0.01752,0.13322]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47086,0.04607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"contact_descend","phase_type":"descend","tcp_position_centroid":[0.39673,0.02406,0.14147]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47086,0.04607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39716,0.02397,0.14105]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.47086,0.04607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.43121,0.03451,0.16155]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47086,0.04607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"arc_approach_goal","phase_type":"approach","tcp_position_centroid":[0.47318,0.05902,0.31559]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.47086,0.04607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52519,0.10928,0.33127]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47086,0.04607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53723,0.11745,0.31036]},{"body_a":"left_finger","body_b":"right_finger","contact_count":750.0,"contact_point_centroid":[0.39918,0.02392,0.13985],"force_p95":0.01341,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01096,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.39724,0.02394,0.1409]}],"total_contact_groups":21},"final_pose_error":0.17845,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.47086,0.04607,0.01602],"final_tcp_position":[0.53636,0.11731,0.30812],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9749.08761,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":195.15179,"phase_name":"arc_approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4824.0,"raw_peak_contact_force":1552.10831,"subtask_id":"approach_object","tcp_end":[0.39673,0.02406,0.14147],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14737,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.47086,0.04607,0.01602],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.23914,"object_z_max":0.01602,"peak_contact_force":127.7389,"phase_name":"contact_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":95.22685,"subtask_id":"grasp_object","tcp_end":[0.39674,0.02406,0.14146],"tcp_start":[0.39673,0.02406,0.14147],"tcp_to_object_dist_end":0.14736,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.47086,0.04607,0.01602],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.23914,"object_z_max":0.01602,"peak_contact_force":68.39528,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3500.0,"raw_peak_contact_force":86.72691,"tcp_end":[0.39725,0.02393,0.14089],"tcp_start":[0.39725,0.02394,0.14089],"tcp_to_object_dist_end":0.14664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.47086,0.04607,0.01602],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.23914,"object_z_max":0.01602,"peak_contact_force":9749.08761,"phase_name":"lift_object_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2397.0,"raw_peak_contact_force":279.3346,"subtask_id":"lift_object","tcp_end":[0.46082,0.04387,0.18044],"tcp_start":[0.45969,0.04324,0.17986],"tcp_to_object_dist_end":0.16474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.47086,0.04607,0.01602],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.23914,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"arc_approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8282.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50717,0.10036,0.37338],"tcp_start":[0.46082,0.04387,0.18044],"tcp_to_object_dist_end":0.36328,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.47086,0.04607,0.01602],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.23914,"object_z_max":0.01602,"peak_contact_force":218.2075,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3764.0,"raw_peak_contact_force":297.95528,"subtask_id":"place_at_goal","tcp_end":[0.53636,0.11731,0.30812],"tcp_start":[0.50717,0.10036,0.37338],"tcp_to_object_dist_end":0.30772,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47086,0.04607,0.01602],"object_pos_start":[0.47086,0.04607,0.01602],"object_to_goal_dist_end":0.23914,"object_to_goal_dist_start":0.23914,"object_z_max":0.01602,"peak_contact_force":51.67342,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1227.0,"raw_peak_contact_force":217.35218,"tcp_end":[0.53776,0.1175,0.33028],"tcp_start":[0.53636,0.11731,0.30812],"tcp_to_object_dist_end":0.32914,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":46.0,"average_failure_rate":0.17829,"average_mean_iterations":39.1124,"average_solve_count":258.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach_goal.arc_height":0.0743,"arc_approach_goal.speed":0.03868,"arc_approach_object.arc_height":0.19572,"arc_approach_object.speed":0.03416,"contact_descend.force_threshold":4.62174,"contact_descend.speed":0.02789,"descend_place.speed":0.04904,"grasp.grasp_duration":0.73481,"lift_object_up.lift_height":0.23711,"lift_object_up.speed":0.0748,"release.release_duration":0.61492},"optimized_scores":{"best_composite_score":-0.38984,"best_fitness_score":0.1673,"best_task_score":0.12415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62653,0.02011,-0.00047],"force_p95":204.05125,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1323.89258,"mean_force":208.01724,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.38016,0.01869,0.11376]},{"body_a":"link5","body_b":"hand","contact_count":227.0,"contact_point_centroid":[0.54864,0.06967,0.32501],"force_p95":268.18775,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.1501,"mean_force":233.5247,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52192,0.16393,0.33931]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.5477,0.08286,0.28965],"force_p95":212.81308,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.96163,"mean_force":115.79009,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53319,0.17468,0.32769]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62209,0.02617,-0.00026],"force_p95":110.42507,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.42507,"mean_force":110.42507,"phase_index":1.0,"phase_name":"contact_descend","phase_type":"descend","tcp_position_centroid":[0.38227,0.02584,0.13017]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.62311,0.02609,-0.0001],"force_p95":78.26603,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.54715,"mean_force":22.23405,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.3829,0.02577,0.12975]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62294,0.02611,-0.00013],"force_p95":84.74331,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.40443,"mean_force":71.98307,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.38274,0.02577,0.12971]},{"body_a":"grasp_target","body_b":"hand","contact_count":56.0,"contact_point_centroid":[0.4588,0.04206,0.04132],"force_p95":3.79172,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91317,"mean_force":1.53808,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.37576,0.01308,0.06291]},{"body_a":"grasp_target","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.48073,0.02909,0.01687],"force_p95":2.82334,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.28916,"mean_force":0.63083,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.37055,0.01307,0.06713]},{"body_a":"world","body_b":"grasp_target","contact_count":3841.0,"contact_point_centroid":[0.44703,0.04957,-0.00221],"force_p95":0.18731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.30706,"mean_force":0.14495,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.39342,0.01782,0.12481]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44106,0.04966,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"contact_descend","phase_type":"descend","tcp_position_centroid":[0.38227,0.02584,0.13017]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44106,0.04966,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.38274,0.02577,0.12971]},{"body_a":"world","body_b":"grasp_target","contact_count":1692.0,"contact_point_centroid":[0.44106,0.04966,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.40994,0.03748,0.1867]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44106,0.04966,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"arc_approach_goal","phase_type":"approach","tcp_position_centroid":[0.46926,0.0955,0.3544]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.44106,0.04966,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51381,0.15548,0.35601]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44106,0.04966,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53319,0.17468,0.32769]},{"body_a":"left_finger","body_b":"right_finger","contact_count":753.0,"contact_point_centroid":[0.3849,0.02574,0.12865],"force_p95":0.01344,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01517,"mean_force":0.01093,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.38284,0.02574,0.12954]}],"total_contact_groups":21},"final_pose_error":0.10484,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44106,0.04966,0.01602],"final_tcp_position":[0.5319,0.17501,0.32529],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273004.12048,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":203.8096,"phase_name":"arc_approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4853.0,"raw_peak_contact_force":1323.89258,"subtask_id":"approach_object","tcp_end":[0.38227,0.02584,0.13017],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13059,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.44106,0.04966,0.01602],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31294,"object_z_max":0.01602,"peak_contact_force":140.39633,"phase_name":"contact_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":110.42507,"subtask_id":"grasp_object","tcp_end":[0.38227,0.02585,0.13016],"tcp_start":[0.38227,0.02584,0.13017],"tcp_to_object_dist_end":0.13058,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.44106,0.04966,0.01602],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31294,"object_z_max":0.01602,"peak_contact_force":67.92925,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":90.40443,"tcp_end":[0.38284,0.02573,0.12953],"tcp_start":[0.38284,0.02573,0.12954],"tcp_to_object_dist_end":0.1298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.44106,0.04966,0.01602],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31294,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3471.0,"raw_peak_contact_force":91.54715,"subtask_id":"lift_object","tcp_end":[0.43449,0.04768,0.23685],"tcp_start":[0.43409,0.04741,0.23614],"tcp_to_object_dist_end":0.22094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.44106,0.04966,0.01602],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31294,"object_z_max":0.01602,"peak_contact_force":9748.82849,"phase_name":"arc_approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8294.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49294,0.13349,0.39971],"tcp_start":[0.43449,0.04768,0.23685],"tcp_to_object_dist_end":0.39615,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.44106,0.04966,0.01602],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31294,"object_z_max":0.01602,"peak_contact_force":259.95524,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3478.0,"raw_peak_contact_force":291.1501,"subtask_id":"place_at_goal","tcp_end":[0.5319,0.17501,0.32529],"tcp_start":[0.49294,0.13349,0.39971],"tcp_to_object_dist_end":0.34585,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44106,0.04966,0.01602],"object_pos_start":[0.44106,0.04966,0.01602],"object_to_goal_dist_end":0.31294,"object_to_goal_dist_start":0.31294,"object_z_max":0.01602,"peak_contact_force":38.91513,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1225.0,"raw_peak_contact_force":218.96163,"tcp_end":[0.53382,0.17456,0.34752],"tcp_start":[0.5319,0.17501,0.32529],"tcp_to_object_dist_end":0.36619,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.74211,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach_goal.arc_height":0.12262,"arc_approach_goal.speed":0.06868,"arc_approach_object.arc_height":0.05767,"arc_approach_object.speed":0.04465,"contact_descend.force_threshold":3.81678,"contact_descend.speed":0.02252,"descend_place.speed":0.02786,"grasp.grasp_duration":1.9999,"lift_object_up.lift_height":0.23993,"lift_object_up.speed":0.06479,"release.release_duration":0.57351},"optimized_scores":{"best_composite_score":-0.39607,"best_fitness_score":0.16107,"best_task_score":0.10763},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":151.0,"contact_point_centroid":[0.58611,-0.08785,-0.00129],"force_p95":264.00042,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1357.72567,"mean_force":148.89555,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.45562,-0.06795,0.07949]},{"body_a":"world","body_b":"link6","contact_count":381.0,"contact_point_centroid":[0.68356,0.0052,-0.00043],"force_p95":271.10194,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.23225,"mean_force":212.55925,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.4565,-0.07424,0.10005]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68763,-0.00182,-0.00019],"force_p95":334.23121,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.23121,"mean_force":334.23121,"phase_index":1.0,"phase_name":"contact_descend","phase_type":"descend","tcp_position_centroid":[0.45637,-0.08304,0.12009]},{"body_a":"link5","body_b":"hand","contact_count":914.0,"contact_point_centroid":[0.53961,0.08859,0.37129],"force_p95":81.39552,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.87257,"mean_force":72.98482,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53653,0.00284,0.30282]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.6882,-0.00208,-0.00013],"force_p95":79.75634,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.03466,"mean_force":69.44005,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45659,-0.08322,0.11959]},{"body_a":"link5","body_b":"hand","contact_count":884.0,"contact_point_centroid":[0.53104,0.03852,0.2688],"force_p95":98.94168,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.60986,"mean_force":69.01189,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.49171,-0.03883,0.19831]},{"body_a":"link5","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.52788,0.04468,0.37787],"force_p95":70.85675,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.30488,"mean_force":68.41314,"phase_index":4.0,"phase_name":"arc_approach_goal","phase_type":"approach","tcp_position_centroid":[0.50761,-0.03127,0.30007]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.6883,-0.00205,-0.0001],"force_p95":75.7203,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.92722,"mean_force":31.41746,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.45664,-0.08316,0.11958]},{"body_a":"grasp_target","body_b":"hand","contact_count":80.0,"contact_point_centroid":[0.5192,-0.02616,0.03641],"force_p95":3.90866,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.36526,"mean_force":1.10842,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.45347,-0.04561,0.05144]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.50792,-0.02211,-0.00233],"force_p95":0.39306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74023,"mean_force":0.16176,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.4727,-0.06321,0.1261]},{"body_a":"grasp_target","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.54852,-0.00473,0.01252],"force_p95":0.78189,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.80855,"mean_force":0.46846,"phase_index":0.0,"phase_name":"arc_approach_object","phase_type":"approach","tcp_position_centroid":[0.4477,-0.04274,0.03575]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49795,-0.02233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"contact_descend","phase_type":"descend","tcp_position_centroid":[0.45637,-0.08304,0.12009]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49795,-0.02233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45659,-0.08322,0.11959]},{"body_a":"world","body_b":"grasp_target","contact_count":4344.0,"contact_point_centroid":[0.49795,-0.02233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object_up","phase_type":"lift","tcp_position_centroid":[0.48644,-0.04475,0.18808]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49795,-0.02233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"arc_approach_goal","phase_type":"approach","tcp_position_centroid":[0.50761,-0.03127,0.30007]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49795,-0.02233,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53687,0.00456,0.30228]}],"total_contact_groups":23},"final_pose_error":0.22447,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49795,-0.02233,0.01602],"final_tcp_position":[0.54043,0.02559,0.29547],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.12097,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":205.26564,"phase_name":"arc_approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2692.0,"raw_peak_contact_force":1357.72567,"subtask_id":"approach_object","tcp_end":[0.45637,-0.08304,0.12009],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12746,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.49795,-0.02233,0.01602],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.33436,"object_z_max":0.01602,"peak_contact_force":334.23121,"phase_name":"contact_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":334.23121,"subtask_id":"grasp_object","tcp_end":[0.45638,-0.08307,0.12013],"tcp_start":[0.45637,-0.08304,0.12009],"tcp_to_object_dist_end":0.1275,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.49795,-0.02233,0.01602],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.33436,"object_z_max":0.01602,"peak_contact_force":273004.12091,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3501.0,"raw_peak_contact_force":138.03466,"tcp_end":[0.45663,-0.08323,0.11943],"tcp_start":[0.45663,-0.08323,0.11943],"tcp_to_object_dist_end":0.12693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1086.0,"n_steps_budget":1000.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.49795,-0.02233,0.01602],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.33436,"object_z_max":0.01602,"peak_contact_force":59.4746,"phase_name":"lift_object_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10030.0,"raw_peak_contact_force":127.60986,"subtask_id":"lift_object","tcp_end":[0.49896,-0.02421,0.23682],"tcp_start":[0.49959,-0.02442,0.23614],"tcp_to_object_dist_end":0.22081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.49795,-0.02233,0.01602],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.33436,"object_z_max":0.01602,"peak_contact_force":53.24494,"phase_name":"arc_approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9502.0,"raw_peak_contact_force":118.30488,"tcp_end":[0.52164,-0.02728,0.3275],"tcp_start":[0.49896,-0.02421,0.23682],"tcp_to_object_dist_end":0.31242,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.49795,-0.02233,0.01602],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.33436,"object_z_max":0.01602,"peak_contact_force":9749.34331,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9407.0,"raw_peak_contact_force":143.87257,"subtask_id":"place_at_goal","tcp_end":[0.54043,0.02559,0.29547],"tcp_start":[0.52164,-0.02728,0.3275],"tcp_to_object_dist_end":0.28669,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49795,-0.02233,0.01602],"object_pos_start":[0.49795,-0.02233,0.01602],"object_to_goal_dist_end":0.33436,"object_to_goal_dist_start":0.33436,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54008,0.02639,0.31625],"tcp_start":[0.54043,0.02559,0.29547],"tcp_to_object_dist_end":0.30706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```