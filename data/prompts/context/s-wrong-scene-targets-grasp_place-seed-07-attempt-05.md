## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.0099 | 0.32 | ✅ accepted |
| 4 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.5365 | 0.17 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.3864 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.010) — your mutation base

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

- **Composite score**: -0.010
- **task_score** (E): 0.323
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 0.00 | 1.00 | 0.0001 |
| descend_to_grasp | 1.00 | 1.00 | 0.2465 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1274 |
| approach_goal | 1.00 | 1.00 | 0.2796 |
| descend_place | 1.00 | 1.00 | 0.1478 |
| release | 1.00 | 1.00 | 0.0200 |
| retract | 1.00 | 1.00 | 0.1326 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, 0.000, 0.301) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.030) | 0.271→0.271 | 1.00 / 4.000 | 0.000 | 0.000 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.500, 0.000, 0.301)→(0.506, 0.021, 0.058) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 8.706 | 0.138 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.021, 0.058)→(0.498, 0.021, 0.049) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 39.667 | 0.196 | 0.239 |
| lift | lift | 1.00 / step_budget | (0.498, 0.021, 0.049)→(0.506, 0.021, 0.176) | (0.511, 0.021, 0.025)→(0.512, 0.022, 0.148) | 0.274→0.222 | 1.00 / 30.667 | 0.105 | 0.395 |
| approach_goal | approach | 1.00 / step_budget | (0.506, 0.021, 0.176)→(0.598, 0.195, 0.370) | (0.512, 0.022, 0.148)→(0.599, 0.188, 0.225) | 0.222→0.161 | 1.00 / 15.000 | 91007.383 | 0.902 |
| descend_place | descend | 1.00 / step_budget | (0.598, 0.195, 0.370)→(0.603, 0.207, 0.223) | (0.599, 0.188, 0.225)→(0.599, 0.198, 0.059) | 0.161→0.137 | 1.00 / 12.333 | 0.121 | 0.972 |
| release | release | 1.00 / step_budget | (0.603, 0.207, 0.223)→(0.598, 0.205, 0.242) | (0.599, 0.198, 0.059)→(0.595, 0.198, 0.023) | 0.137→0.173 | 1.00 / 3.333 | 0.143 | 0.581 |
| retract | retract | 1.00 / step_budget | (0.598, 0.205, 0.242)→(0.605, 0.209, 0.374) | (0.595, 0.198, 0.023)→(0.591, 0.198, 0.023) | 0.173→0.174 | 1.00 / 4.000 | 0.123 | 0.167 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.445
- phase_score: 0.597
- phase_breakdown.approach_object_score: 0.078
- phase_breakdown.grasp_object_score: 0.822
- phase_breakdown.lift_object_score: 0.813
- phase_breakdown.place_at_goal_score: 0.823
- grasp_place_fitness: 0.681

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.681
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.445
- **Median Q (composite search score)**: -0.035
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01144,"average_solve_count":437.0,"average_success_count":437.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.06114,"approach_pre_grasp.speed":0.0422,"descend_place.speed":0.02707,"descend_to_grasp.speed":0.02787,"grasp.grasp_duration":1.34366,"lift.lift_height":0.18348,"lift.speed":0.04366,"release.release_duration":0.7921,"retract.speed":0.07348},"optimized_scores":{"best_composite_score":0.0506,"best_fitness_score":0.6806,"best_task_score":0.44492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.61045,0.16885,-0.0067],"force_p95":1.16777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49263,"mean_force":0.35369,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61655,0.16808,0.18117]},{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.50928,0.0358,-0.00176],"force_p95":0.34486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38566,"mean_force":0.11152,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49835,0.03657,0.05054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6153.0,"contact_point_centroid":[0.50229,0.01768,0.10754],"force_p95":0.12221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32476,"mean_force":0.08519,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50122,0.03677,0.10908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3592.0,"contact_point_centroid":[0.62261,0.18236,0.24404],"force_p95":0.13742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29239,"mean_force":0.10997,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61785,0.16414,0.24784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10255.0,"contact_point_centroid":[0.50175,0.05525,0.11752],"force_p95":0.09251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27185,"mean_force":0.05435,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50183,0.03681,0.11723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3795.0,"contact_point_centroid":[0.62259,0.14612,0.24293],"force_p95":0.12679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26816,"mean_force":0.101,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6179,0.16422,0.24634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.62517,0.18772,0.16378],"force_p95":0.10854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26479,"mean_force":0.07757,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62038,0.16935,0.16832]},{"body_a":"world","body_b":"grasp_target","contact_count":2184.0,"contact_point_centroid":[0.60389,0.16952,-0.00203],"force_p95":0.16715,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25497,"mean_force":0.12517,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61949,0.16941,0.25963]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":597.0,"contact_point_centroid":[0.62521,0.15079,0.16352],"force_p95":0.11672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25189,"mean_force":0.08408,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62037,0.16935,0.16829]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5126,0.03964,-0.00227],"force_p95":0.20087,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24582,"mean_force":0.14201,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50052,0.03676,0.05025]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6269.0,"contact_point_centroid":[0.55628,0.11137,0.24644],"force_p95":0.11759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22959,"mean_force":0.0689,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55573,0.09291,0.24765]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4531.0,"contact_point_centroid":[0.5621,0.07881,0.24979],"force_p95":0.12573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22366,"mean_force":0.0923,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55981,0.09752,0.25276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.50023,0.01752,0.04957],"force_p95":0.10568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13903,"mean_force":0.05609,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49938,0.03666,0.04898]},{"body_a":"world","body_b":"grasp_target","contact_count":3340.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50245,0.01849,0.17774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.50018,0.05564,0.04977],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08282,"mean_force":0.04384,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49939,0.03667,0.04899]}],"total_contact_groups":15},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60337,0.16952,0.02602],"final_tcp_position":[0.62501,0.17149,0.32523],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":25.87216,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02996],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21003,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_object","tcp_end":[0.49986,0.0,0.30087],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27409,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02996],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21003,"object_z_max":0.02996,"peak_contact_force":25.87216,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3340.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_object","tcp_end":[0.50732,0.03724,0.05795],"tcp_start":[0.49986,0.0,0.30087],"tcp_to_object_dist_end":0.03245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03762,0.02483],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2142,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.20301,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10806.0,"raw_peak_contact_force":0.24582,"tcp_end":[0.49935,0.03666,0.04894],"tcp_start":[0.50732,0.03724,0.05795],"tcp_to_object_dist_end":0.02748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.51374,0.0388,0.15981],"object_pos_start":[0.51251,0.03762,0.02483],"object_to_goal_dist_end":0.17623,"object_to_goal_dist_start":0.2142,"object_z_max":0.15955,"peak_contact_force":0.12062,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16511.0,"raw_peak_contact_force":0.38566,"subtask_id":"lift_object","tcp_end":[0.50798,0.03726,0.18897],"tcp_start":[0.49935,0.03666,0.04894],"tcp_to_object_dist_end":0.02976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.62196,0.16075,0.28933],"object_pos_start":[0.51374,0.0388,0.15981],"object_to_goal_dist_end":0.14489,"object_to_goal_dist_start":0.17623,"object_z_max":0.28906,"peak_contact_force":0.12858,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.22959,"tcp_end":[0.61493,0.15917,0.32182],"tcp_start":[0.50798,0.03726,0.18897],"tcp_to_object_dist_end":0.03328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.62736,0.16995,0.13602],"object_pos_start":[0.62196,0.16075,0.28933],"object_to_goal_dist_end":0.00937,"object_to_goal_dist_start":0.14489,"object_z_max":0.28954,"peak_contact_force":0.11669,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7387.0,"raw_peak_contact_force":0.29239,"subtask_id":"place_at_goal","tcp_end":[0.6225,0.16993,0.17292],"tcp_start":[0.61493,0.15917,0.32182],"tcp_to_object_dist_end":0.03722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61448,0.1675,0.02747],"object_pos_start":[0.62736,0.16995,0.13602],"object_to_goal_dist_end":0.11838,"object_to_goal_dist_start":0.00937,"object_z_max":0.13602,"peak_contact_force":0.18349,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1449.0,"raw_peak_contact_force":1.49263,"tcp_end":[0.61649,0.16806,0.19194],"tcp_start":[0.6225,0.16993,0.17292],"tcp_to_object_dist_end":0.16448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.60337,0.16952,0.02602],"object_pos_start":[0.61448,0.1675,0.02747],"object_to_goal_dist_end":0.12148,"object_to_goal_dist_start":0.11838,"object_z_max":0.02841,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.25497,"tcp_end":[0.62501,0.17149,0.32523],"tcp_start":[0.61649,0.16806,0.19194],"tcp_to_object_dist_end":0.3,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07895,"average_solve_count":418.0,"average_success_count":418.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.05898,"approach_pre_grasp.speed":0.05361,"descend_place.speed":0.04456,"descend_to_grasp.speed":0.02823,"grasp.grasp_duration":1.12109,"lift.lift_height":0.16489,"lift.speed":0.03928,"release.release_duration":0.46676,"retract.speed":0.08237},"optimized_scores":{"best_composite_score":-0.0449,"best_fitness_score":0.5851,"best_task_score":0.25509},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.57361,0.24121,-0.00475],"force_p95":1.05422,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.49891,"mean_force":0.23807,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57763,0.22409,0.28698]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.47951,0.04414,-0.00172],"force_p95":0.34852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43418,"mean_force":0.12753,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47071,0.04489,0.052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.57636,0.19957,0.37716],"force_p95":0.17419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34369,"mean_force":0.1119,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57466,0.21728,0.3821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1141.0,"contact_point_centroid":[0.57757,0.2352,0.37541],"force_p95":0.15749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31827,"mean_force":0.11381,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57471,0.2174,0.38033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.47265,0.02604,0.10445],"force_p95":0.12314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2941,"mean_force":0.08589,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47308,0.04511,0.10672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8047.0,"contact_point_centroid":[0.47296,0.06358,0.10761],"force_p95":0.09657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28119,"mean_force":0.05715,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4731,0.04511,0.10752]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.0485,-0.00227],"force_p95":0.24722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2599,"mean_force":0.17047,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47277,0.04509,0.05185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7348.0,"contact_point_centroid":[0.51802,0.13813,0.26791],"force_p95":0.12416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19956,"mean_force":0.08416,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5187,0.11969,0.27067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6658.0,"contact_point_centroid":[0.52155,0.10848,0.27803],"force_p95":0.12246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18555,"mean_force":0.08958,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5229,0.12701,0.28082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2870.0,"contact_point_centroid":[0.47163,0.0259,0.04868],"force_p95":0.11861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18363,"mean_force":0.08221,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47168,0.04499,0.05071]},{"body_a":"world","body_b":"grasp_target","contact_count":3280.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48855,0.02264,0.1783]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57344,0.23959,-0.00199],"force_p95":0.12652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12738,"mean_force":0.12259,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57561,0.22489,0.25978]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.57344,0.23959,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12267,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57682,0.22577,0.34436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5157.0,"contact_point_centroid":[0.47157,0.06385,0.05102],"force_p95":0.0849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09624,"mean_force":0.04969,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4717,0.04499,0.05072]},{"body_a":"left_finger","body_b":"right_finger","contact_count":521.0,"contact_point_centroid":[0.57815,0.22457,0.28347],"force_p95":0.01464,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01098,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57783,0.22454,0.28128]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57761,0.2258,0.25794],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57735,0.22577,0.25581]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57344,0.23959,0.02602],"final_tcp_position":[0.58079,0.22797,0.41058],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.49891,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02996],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28721,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_object","tcp_end":[0.49986,0.0,0.30087],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27579,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02996],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28721,"object_z_max":0.02996,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3280.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_object","tcp_end":[0.47932,0.04564,0.05879],"tcp_start":[0.49986,0.0,0.30087],"tcp_to_object_dist_end":0.03309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04604,0.02508],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29231,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.23332,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9827.0,"raw_peak_contact_force":0.2599,"tcp_end":[0.47166,0.04499,0.05068],"tcp_start":[0.47932,0.04564,0.05879],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.48303,0.04709,0.14163],"object_pos_start":[0.4827,0.04604,0.02508],"object_to_goal_dist_end":0.22517,"object_to_goal_dist_start":0.29231,"object_z_max":0.14136,"peak_contact_force":0.11449,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13043.0,"raw_peak_contact_force":0.43418,"subtask_id":"lift_object","tcp_end":[0.47815,0.0456,0.17073],"tcp_start":[0.47166,0.04499,0.05068],"tcp_to_object_dist_end":0.02954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.5779,0.21694,0.37043],"object_pos_start":[0.48303,0.04709,0.14163],"object_to_goal_dist_end":0.14051,"object_to_goal_dist_start":0.22517,"object_z_max":0.3701,"peak_contact_force":0.14841,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14006.0,"raw_peak_contact_force":0.19956,"tcp_end":[0.57437,0.21591,0.40472],"tcp_start":[0.47815,0.0456,0.17073],"tcp_to_object_dist_end":0.03449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.57334,0.23886,0.02599],"object_pos_start":[0.5779,0.21694,0.37043],"object_to_goal_dist_end":0.20491,"object_to_goal_dist_start":0.14051,"object_z_max":0.37068,"peak_contact_force":0.12498,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3403.0,"raw_peak_contact_force":2.49891,"subtask_id":"place_at_goal","tcp_end":[0.5786,0.22626,0.25948],"tcp_start":[0.57437,0.21591,0.40472],"tcp_to_object_dist_end":0.23389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57344,0.23959,0.02602],"object_pos_start":[0.57334,0.23886,0.02599],"object_to_goal_dist_end":0.20492,"object_to_goal_dist_start":0.20491,"object_z_max":0.02603,"peak_contact_force":0.12264,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12738,"tcp_end":[0.57466,0.22437,0.27948],"tcp_start":[0.5786,0.22626,0.25948],"tcp_to_object_dist_end":0.25392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.57344,0.23959,0.02602],"object_pos_start":[0.57344,0.23959,0.02602],"object_to_goal_dist_end":0.20492,"object_to_goal_dist_start":0.20492,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12267,"tcp_end":[0.58079,0.22797,0.41058],"tcp_start":[0.57466,0.22437,0.27948],"tcp_to_object_dist_end":0.38481,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22161,"average_solve_count":361.0,"average_success_count":361.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.13926,"approach_pre_grasp.speed":0.0681,"descend_place.speed":0.03211,"descend_to_grasp.speed":0.04936,"grasp.grasp_duration":1.43008,"lift.lift_height":0.16211,"lift.speed":0.03927,"release.release_duration":0.32462,"retract.speed":0.10347},"optimized_scores":{"best_composite_score":-0.03532,"best_fitness_score":0.59468,"best_task_score":0.26988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.59696,0.18552,-0.00401],"force_p95":1.00534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27753,"mean_force":0.22647,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59517,0.18079,0.35521]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.53367,-0.02017,-0.00152],"force_p95":0.33784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36417,"mean_force":0.12258,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52119,-0.01998,0.0484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4659.0,"contact_point_centroid":[0.55189,0.05595,0.21859],"force_p95":0.11856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32011,"mean_force":0.07393,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54796,0.03714,0.21874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9200.0,"contact_point_centroid":[0.52592,-0.03918,0.10788],"force_p95":0.081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25006,"mean_force":0.0543,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52523,-0.02011,0.10686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8280.0,"contact_point_centroid":[0.52601,-0.00097,0.10794],"force_p95":0.08248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24409,"mean_force":0.05897,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52523,-0.02011,0.10686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4643.0,"contact_point_centroid":[0.55096,0.0155,0.21635],"force_p95":0.12399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24286,"mean_force":0.07286,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54704,0.03427,0.21604]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02124,-0.00211],"force_p95":0.15442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21186,"mean_force":0.13101,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52336,-0.02002,0.04878]},{"body_a":"world","body_b":"grasp_target","contact_count":3416.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.51402,-0.01001,0.17713]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4338.0,"contact_point_centroid":[0.52333,-0.0008,0.04861],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12761,"mean_force":0.04952,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52217,-0.01999,0.04738]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.59581,0.18583,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12345,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60573,0.21723,0.31098]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59581,0.18583,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60368,0.22323,0.23569]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.59581,0.18583,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60487,0.22437,0.32091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.52321,-0.03916,0.0486],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07368,"mean_force":0.04426,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52217,-0.01999,0.04739]},{"body_a":"left_finger","body_b":"right_finger","contact_count":578.0,"contact_point_centroid":[0.59692,0.18506,0.36155],"force_p95":0.01364,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01088,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59661,0.18506,0.35929]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1744.0,"contact_point_centroid":[0.60621,0.21726,0.31321],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60574,0.21724,0.31089]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.60617,0.22419,0.23452],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60564,0.22416,0.2322]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59581,0.18583,0.01602],"final_tcp_position":[0.60912,0.22684,0.3876],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273021.87211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02996],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31448,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_object","tcp_end":[0.49986,0.0,0.30087],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27427,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02996],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31448,"object_z_max":0.02996,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3416.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_object","tcp_end":[0.5304,-0.02011,0.05714],"tcp_start":[0.49986,0.0,0.30087],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53698,-0.02042,0.02559],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31627,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15168,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11110.0,"raw_peak_contact_force":0.21186,"tcp_end":[0.52214,-0.01999,0.04735],"tcp_start":[0.5304,-0.02011,0.05714],"tcp_to_object_dist_end":0.02634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.54049,-0.02055,0.14289],"object_pos_start":[0.53698,-0.02042,0.02559],"object_to_goal_dist_end":0.26588,"object_to_goal_dist_start":0.31627,"object_z_max":0.14265,"peak_contact_force":0.07874,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17578.0,"raw_peak_contact_force":0.36417,"subtask_id":"lift_object","tcp_end":[0.53192,-0.0203,0.16861],"tcp_start":[0.52214,-0.01999,0.04735],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.59581,0.18583,0.016],"object_pos_start":[0.54049,-0.02055,0.14289],"object_to_goal_dist_end":0.19648,"object_to_goal_dist_start":0.26588,"object_z_max":0.25384,"peak_contact_force":273021.87211,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10504.0,"raw_peak_contact_force":2.27753,"tcp_end":[0.60518,0.21081,0.38369],"tcp_start":[0.53192,-0.0203,0.16861],"tcp_to_object_dist_end":0.36865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.59581,0.18583,0.01602],"object_pos_start":[0.59581,0.18583,0.016],"object_to_goal_dist_end":0.19647,"object_to_goal_dist_start":0.19648,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.12345,"subtask_id":"place_at_goal","tcp_end":[0.60703,0.22464,0.23616],"tcp_start":[0.60518,0.21081,0.38369],"tcp_to_object_dist_end":0.22382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59581,0.18583,0.01602],"object_pos_start":[0.59581,0.18583,0.01602],"object_to_goal_dist_end":0.19647,"object_to_goal_dist_start":0.19647,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60258,0.22268,0.25506],"tcp_start":[0.60703,0.22464,0.23616],"tcp_to_object_dist_end":0.24196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":930.0,"object_pos_end":[0.59581,0.18583,0.01602],"object_pos_start":[0.59581,0.18583,0.01602],"object_to_goal_dist_end":0.19647,"object_to_goal_dist_start":0.19647,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60912,0.22684,0.3876],"tcp_start":[0.60258,0.22268,0.25506],"tcp_to_object_dist_end":0.37407,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```