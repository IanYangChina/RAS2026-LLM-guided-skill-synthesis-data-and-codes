## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2528 | 0.33 | ✅ accepted |
| 3 | descend → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14  | -0.2841 | 0.17 | ❌ rejected |
| 2 | descend → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.2211 | 0.19 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6  | -0.2211 | 0.19 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.1669 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.747, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.167) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_grasp_height
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_above
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_goal
  weight: 0.3
phases:
- id: descend_approach
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp_height
- id: grasp_object
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
    tolerance: 0.005
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: reach_grasp_height
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
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
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_above
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_height_offset:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_approach** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.167
- **task_score** (E): 0.747
- **fitness_score**: 0.837  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1354 |
| descend_to_grasp | 1.00 | 1.00 | 0.1164 |
| grasp_object | 1.00 | 1.00 | 0.0121 |
| lift_object | 1.00 | 1.00 | 0.1047 |
| transport_to_goal | 1.00 | 1.00 | 0.2359 |
| descend_to_place | 1.00 | 1.00 | 0.0492 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.018, 0.171) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.018, 0.171)→(0.506, 0.022, 0.054) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 7.896 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.022, 0.054)→(0.498, 0.021, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 42.333 | 0.154 | 0.211 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.045)→(0.506, 0.021, 0.150) | (0.511, 0.022, 0.026)→(0.514, 0.022, 0.127) | 0.274→0.226 | 1.00 / 38.333 | 0.083 | 0.349 |
| transport_to_goal | approach | 1.00 / step_budget | (0.506, 0.021, 0.150)→(0.592, 0.187, 0.281) | (0.514, 0.022, 0.127)→(0.590, 0.164, 0.174) | 0.226→0.118 | 1.00 / 20.667 | 3249.691 | 0.742 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.187, 0.281)→(0.600, 0.202, 0.235) | (0.590, 0.164, 0.174)→(0.598, 0.175, 0.138) | 0.118→0.080 | 1.00 / 18.000 | 0.118 | 0.250 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.483
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.508
- phase_breakdown.reach_grasp_height_score: 0.673
- phase_breakdown.lift_clearance_score: 0.554
- phase_breakdown.reach_goal_score: 0.471
- phase_breakdown.transport_above_score: 0.548
- phase_breakdown.reach_approach_score: 0.331
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.292
- **K-run variance**: 0.0317
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.grasp_height
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81201,"average_solve_count":383.0,"average_success_count":383.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.13684,"descend_approach.approach_speed":0.06617,"descend_to_grasp.descend_speed":0.02982,"descend_to_grasp.grasp_height":0.02006,"descend_to_place.place_height_offset":0.02538,"descend_to_place.place_speed":0.0196,"lift_object.lift_height":0.1448,"lift_object.lift_speed":0.03417,"transport_to_goal.arc_height":0.16925,"transport_to_goal.transport_height":0.0759,"transport_to_goal.transport_speed":0.03523},"optimized_scores":{"best_composite_score":0.29337,"best_fitness_score":0.96337,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.50933,0.03776,-0.00159],"force_p95":0.35712,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38497,"mean_force":0.14485,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49841,0.0379,0.0463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.61846,0.18103,0.20294],"force_p95":0.1005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32959,"mean_force":0.07214,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61521,0.16215,0.20367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.61774,0.1434,0.20328],"force_p95":0.09935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2721,"mean_force":0.07072,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61514,0.16207,0.20412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8645.0,"contact_point_centroid":[0.5013,0.057,0.09731],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25679,"mean_force":0.04975,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50147,0.0379,0.09527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7291.0,"contact_point_centroid":[0.50102,0.01868,0.09816],"force_p95":0.08215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23325,"mean_force":0.05642,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50157,0.03791,0.09614]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03959,-0.00214],"force_p95":0.16295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22247,"mean_force":0.13324,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50054,0.03809,0.0466]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.51251,0.03972,-0.00186],"force_p95":0.13692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50287,0.01544,0.24378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4331.0,"contact_point_centroid":[0.49971,0.01876,0.04726],"force_p95":0.07798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13833,"mean_force":0.04958,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49938,0.03799,0.04532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13174.0,"contact_point_centroid":[0.54689,0.10308,0.21115],"force_p95":0.07706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12956,"mean_force":0.05218,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54601,0.084,0.20989]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50589,0.03544,0.11868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12985.0,"contact_point_centroid":[0.54712,0.06609,0.21194],"force_p95":0.07857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12157,"mean_force":0.05248,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54706,0.08518,0.21097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5261.0,"contact_point_centroid":[0.49991,0.05717,0.04747],"force_p95":0.07166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07389,"mean_force":0.04227,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49939,0.03799,0.04533]}],"total_contact_groups":12},"final_pose_error":0.01487,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62708,0.16681,0.15364],"final_tcp_position":[0.61933,0.16667,0.18132],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":23.44231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":960.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50728,0.0325,0.18462],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":23.44231,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50744,0.03863,0.05435],"tcp_start":[0.50728,0.0325,0.18462],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03849,0.02548],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21331,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15928,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11392.0,"raw_peak_contact_force":0.22247,"subtask_id":"reach_grasp_height","tcp_end":[0.49936,0.03799,0.04529],"tcp_start":[0.50744,0.03863,0.05435],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.51641,0.03849,0.12864],"object_pos_start":[0.51248,0.03849,0.02548],"object_to_goal_dist_end":0.17489,"object_to_goal_dist_start":0.21331,"object_z_max":0.12838,"peak_contact_force":0.08212,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16035.0,"raw_peak_contact_force":0.38497,"subtask_id":"lift_clearance","tcp_end":[0.5073,0.03812,0.15098],"tcp_start":[0.49936,0.03799,0.04529],"tcp_to_object_dist_end":0.02412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.61955,0.15894,0.19553],"object_pos_start":[0.51641,0.03849,0.12864],"object_to_goal_dist_end":0.05291,"object_to_goal_dist_start":0.17489,"object_z_max":0.21086,"peak_contact_force":0.08877,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26159.0,"raw_peak_contact_force":0.12956,"subtask_id":"transport_above","tcp_end":[0.61336,0.15881,0.22239],"tcp_start":[0.5073,0.03812,0.15098],"tcp_to_object_dist_end":0.02756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.62708,0.16681,0.15364],"object_pos_start":[0.61955,0.15894,0.19553],"object_to_goal_dist_end":0.01035,"object_to_goal_dist_start":0.05291,"object_z_max":0.19553,"peak_contact_force":0.10053,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.32959,"subtask_id":"reach_goal","tcp_end":[0.61933,0.16667,0.18132],"tcp_start":[0.61336,0.15881,0.22239],"tcp_to_object_dist_end":0.02875,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.50302,"average_solve_count":497.0,"average_success_count":497.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.12006,"descend_approach.approach_speed":0.04642,"descend_to_grasp.descend_speed":0.01708,"descend_to_grasp.grasp_height":0.02011,"descend_to_place.place_height_offset":0.03957,"descend_to_place.place_speed":0.0231,"lift_object.lift_height":0.13667,"lift_object.lift_speed":0.01715,"transport_to_goal.arc_height":0.08888,"transport_to_goal.transport_height":0.11185,"transport_to_goal.transport_speed":0.03294},"optimized_scores":{"best_composite_score":0.29212,"best_fitness_score":0.96212,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.47995,0.0465,-0.00171],"force_p95":0.2927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29816,"mean_force":0.13877,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46954,0.04655,0.04772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2202.0,"contact_point_centroid":[0.57266,0.22328,0.31049],"force_p95":0.12399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29675,"mean_force":0.08062,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56661,0.20522,0.31168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1477.0,"contact_point_centroid":[0.57198,0.18681,0.30796],"force_p95":0.13821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24026,"mean_force":0.11289,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56666,0.20532,0.31145]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.0486,-0.00217],"force_p95":0.16809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22777,"mean_force":0.13464,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47172,0.04678,0.04805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7482.0,"contact_point_centroid":[0.47255,0.0656,0.0934],"force_p95":0.08161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21572,"mean_force":0.05254,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47229,0.0466,0.09195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6261.0,"contact_point_centroid":[0.47164,0.02741,0.09377],"force_p95":0.08925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18475,"mean_force":0.05994,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47235,0.0466,0.0925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15747.0,"contact_point_centroid":[0.49658,0.09798,0.25783],"force_p95":0.10039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1646,"mean_force":0.06274,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49395,0.0793,0.25764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14489.0,"contact_point_centroid":[0.49348,0.05685,0.25434],"force_p95":0.12996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16241,"mean_force":0.06939,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49184,0.07572,0.25476]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49086,0.01938,0.23593]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47887,0.04392,0.1113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4538.0,"contact_point_centroid":[0.47003,0.02745,0.04846],"force_p95":0.07584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11516,"mean_force":0.04749,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47063,0.04667,0.04691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5290.0,"contact_point_centroid":[0.47049,0.06593,0.04841],"force_p95":0.07243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07462,"mean_force":0.04233,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47063,0.04667,0.04691]}],"total_contact_groups":12},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5809,0.22079,0.24531],"final_tcp_position":[0.57481,0.2196,0.27896],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.29816,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.4823,0.04078,0.16839],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47829,0.04741,0.05495],"tcp_start":[0.4823,0.04078,0.16839],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04732,0.02541],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29129,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16426,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11628.0,"raw_peak_contact_force":0.22777,"subtask_id":"reach_grasp_height","tcp_end":[0.4706,0.04667,0.04688],"tcp_start":[0.47829,0.04741,0.05495],"tcp_to_object_dist_end":0.02464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.48551,0.04725,0.11928],"object_pos_start":[0.48268,0.04732,0.02541],"object_to_goal_dist_end":0.23374,"object_to_goal_dist_start":0.29129,"object_z_max":0.11902,"peak_contact_force":0.0886,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13867.0,"raw_peak_contact_force":0.29816,"subtask_id":"lift_clearance","tcp_end":[0.47753,0.04687,0.14296],"tcp_start":[0.4706,0.04667,0.04688],"tcp_to_object_dist_end":0.025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56662,0.19425,0.31101],"object_pos_start":[0.48551,0.04725,0.11928],"object_to_goal_dist_end":0.08896,"object_to_goal_dist_start":0.23374,"object_z_max":0.31229,"peak_contact_force":0.16241,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30236.0,"raw_peak_contact_force":0.1646,"subtask_id":"transport_above","tcp_end":[0.56042,0.19314,0.34295],"tcp_start":[0.47753,0.04687,0.14296],"tcp_to_object_dist_end":0.03256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.5809,0.22079,0.24531],"object_pos_start":[0.56662,0.19425,0.31101],"object_to_goal_dist_end":0.0169,"object_to_goal_dist_start":0.08896,"object_z_max":0.31101,"peak_contact_force":0.13117,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3679.0,"raw_peak_contact_force":0.29675,"subtask_id":"reach_goal","tcp_end":[0.57481,0.2196,0.27896],"tcp_start":[0.56042,0.19314,0.34295],"tcp_to_object_dist_end":0.03422,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.71496,"average_solve_count":421.0,"average_success_count":421.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.11153,"descend_approach.approach_speed":0.0202,"descend_to_grasp.descend_speed":0.02371,"descend_to_grasp.grasp_height":0.02,"descend_to_place.place_height_offset":0.02663,"descend_to_place.place_speed":0.0169,"lift_object.lift_height":0.14899,"lift_object.lift_speed":0.03154,"transport_to_goal.arc_height":0.06315,"transport_to_goal.transport_height":0.07423,"transport_to_goal.transport_speed":0.09901},"optimized_scores":{"best_composite_score":-0.08472,"best_fitness_score":0.58528,"best_task_score":0.24199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":995.0,"contact_point_centroid":[0.58489,0.1383,-0.0034],"force_p95":0.64836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93239,"mean_force":0.17803,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58834,0.16408,0.28457]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.53397,-0.02053,-0.00151],"force_p95":0.34786,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36265,"mean_force":0.14734,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52185,-0.02065,0.04494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8199.0,"contact_point_centroid":[0.52567,-0.00146,0.1005],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24403,"mean_force":0.05532,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52541,-0.02061,0.09784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8222.0,"contact_point_centroid":[0.54407,-0.00324,0.21201],"force_p95":0.11786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24055,"mean_force":0.06522,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54034,0.01561,0.21022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8652.0,"contact_point_centroid":[0.52566,-0.0397,0.09899],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23443,"mean_force":0.05315,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52529,-0.02061,0.09675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7727.0,"contact_point_centroid":[0.54501,0.03681,0.21439],"force_p95":0.11659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22805,"mean_force":0.06905,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54107,0.01792,0.2126]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02121,-0.00206],"force_p95":0.14015,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1815,"mean_force":0.12766,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52407,-0.0207,0.04553]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51257,-0.00856,0.23162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4332.0,"contact_point_centroid":[0.52362,-0.00146,0.04698],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13259,"mean_force":0.04933,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52287,-0.02067,0.04413]},{"body_a":"world","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52811,-0.0194,0.10574]},{"body_a":"world","body_b":"grasp_target","contact_count":364.0,"contact_point_centroid":[0.58483,0.13822,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60322,0.21387,0.26334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4906.0,"contact_point_centroid":[0.52376,-0.0398,0.04592],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08369,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52287,-0.02067,0.04413]},{"body_a":"left_finger","body_b":"right_finger","contact_count":918.0,"contact_point_centroid":[0.5908,0.17007,0.28684],"force_p95":0.01227,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01065,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59026,0.17006,0.28466]},{"body_a":"left_finger","body_b":"right_finger","contact_count":393.0,"contact_point_centroid":[0.60362,0.21385,0.26582],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60321,0.21383,0.26348]}],"total_contact_groups":14},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58483,0.13822,0.01602],"final_tcp_position":[0.60504,0.21937,0.24522],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.82186,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52814,-0.01808,0.15905],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1460.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.5312,-0.02082,0.05396],"tcp_start":[0.52814,-0.01808,0.15905],"tcp_to_object_dist_end":0.02855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.0207,0.02577],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13754,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11038.0,"raw_peak_contact_force":0.1815,"subtask_id":"reach_grasp_height","tcp_end":[0.52284,-0.02067,0.04409],"tcp_start":[0.5312,-0.02082,0.05396],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.54137,-0.02064,0.13416],"object_pos_start":[0.53695,-0.0207,0.02577],"object_to_goal_dist_end":0.26799,"object_to_goal_dist_start":0.3164,"object_z_max":0.13391,"peak_contact_force":0.07731,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16953.0,"raw_peak_contact_force":0.36265,"subtask_id":"lift_clearance","tcp_end":[0.53171,-0.02062,0.15554],"tcp_start":[0.52284,-0.02067,0.04409],"tcp_to_object_dist_end":0.02347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.58483,0.13822,0.01602],"object_pos_start":[0.54137,-0.02064,0.13416],"object_to_goal_dist_end":0.21283,"object_to_goal_dist_start":0.26799,"object_z_max":0.24305,"peak_contact_force":9748.82186,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17862.0,"raw_peak_contact_force":1.93239,"subtask_id":"transport_above","tcp_end":[0.60287,0.20965,0.27837],"tcp_start":[0.53171,-0.02062,0.15554],"tcp_to_object_dist_end":0.2725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.58483,0.13822,0.01602],"object_pos_start":[0.58483,0.13822,0.01602],"object_to_goal_dist_end":0.21283,"object_to_goal_dist_start":0.21283,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":757.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60504,0.21937,0.24522],"tcp_start":[0.60287,0.20965,0.27837],"tcp_to_object_dist_end":0.24399,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```